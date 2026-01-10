#!/bin/bash
set -e

show_help() {
  echo """
  Commands
  ---------------------------------------------------------------

  start            : start django
  worker           : start Celery worker
  start_asgi       : use daphne -b ASGI_IP:WSGI_PORT -p SERVER_PORT  ASGI_APPLICATION
  start_wsgi       : use gunicorn -b WSGI_IP:WSGI_PORT -w WSGI_WORKERS WSGI_APPLICATION
  manage           : run django manage.py
  eval             : eval shell command
  bash             : run bash
  """
}

init(){
  # Install PEP+ module if it exists (for development)
  # Check both /app (docker-compose mount) and /openimis-be (docker build)
  PEP_PLUS_PATH=""
  if [ -d "/app/openimis-be-pep_plus_py" ]; then
    PEP_PLUS_PATH="/app/openimis-be-pep_plus_py"
  elif [ -d "/openimis-be/openimis-be-pep_plus_py" ]; then
    PEP_PLUS_PATH="/openimis-be/openimis-be-pep_plus_py"
  fi

  if [ -n "$PEP_PLUS_PATH" ]; then
    echo "Installing PEP+ module from $PEP_PLUS_PATH..."
    pip install -e "$PEP_PLUS_PATH"

    # Add pep_plus to openimis config if not already there
    CONF_FILE="${OPENIMIS_CONF_JSON:-/openimis-be/openimis.json}"
    echo "Adding pep_plus to $CONF_FILE..."
    python3 << EOF
import json
import sys

conf_file = "$CONF_FILE"
pep_plus_path = "$PEP_PLUS_PATH"

try:
    with open(conf_file, 'r') as f:
        config = json.load(f)

    # Check if pep_plus already exists
    module_names = [m['name'] for m in config.get('modules', [])]
    if 'pep_plus' not in module_names:
        # Find position before signal_binding (which should be last)
        insert_pos = len(config['modules'])
        config['modules'].insert(insert_pos, {
            "name": "pep_plus",
            "pip": f"-e {pep_plus_path}"
        })

        with open(conf_file, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ pep_plus added to configuration")
    else:
        print("ℹ️ pep_plus already in configuration")
except Exception as e:
    print(f"⚠️ Could not modify config: {e}")
    sys.exit(0)  # Continue anyway
EOF
  fi

  # Check if legacy tables exist, create them if not
  if [ "${DJANGO_MIGRATE,,}" == "true" ] || [ "${SCHEDULER_AUTOSTART,,}" == "false" ]; then
    echo "Checking if legacy tables exist..."
    python3 << 'CHECKEOF'
import os
import psycopg2
from psycopg2 import sql

try:
    # Get database connection parameters
    db_host = os.getenv('DB_HOST', os.getenv('PSQL_DB_HOST', 'localhost'))
    db_port = os.getenv('DB_PORT', os.getenv('PSQL_DB_PORT', '5432'))
    db_name = os.getenv('DB_NAME', os.getenv('PSQL_DB_NAME', 'imis'))
    db_user = os.getenv('DB_USER', os.getenv('PSQL_DB_USER', 'postgres'))
    db_password = os.getenv('DB_PASSWORD', os.getenv('PSQL_DB_PASSWORD', ''))

    # Connect to database
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if tblUsers exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'tblUsers'
        );
    """)
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        print("📦 Legacy tables not found. Creating them...")

        # Read and execute the SQL script
        sql_file = '/openimis-be/script/create_legacy_tables.sql'
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            cursor.execute(sql_script)
            print("✅ Legacy tables created successfully")
        else:
            print(f"⚠️ SQL script not found at {sql_file}")
            exit(1)
    else:
        print("✅ Legacy tables already exist")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"⚠️ Database check failed: {e}")
    print("⚠️ Will attempt migrations anyway...")
CHECKEOF

    # Run migrations FIRST (before Django apps initialize)
    echo "Running migrations (standalone mode to avoid scheduler)..."
    python /openimis-be/script/run_migrations.py || {
      echo "⚠️ Standalone migration failed"
      echo "⚠️ Please initialize database with SQL dump or fix migration errors"
      echo "⚠️ See: https://github.com/openimis/database_postgresql"
      exit 1
    }
    echo "✅ Migrations completed successfully"
  fi

  # Compile messages and collect static files (moved from Dockerfile)
  if [ ! -f /openimis-be/.init_done ]; then
    echo "Compiling messages..."
    python manage.py compilemessages -x zh_Hans || echo "Warning: compilemessages failed"
    echo "Collecting static files..."
    python manage.py collectstatic --clear --noinput || echo "Warning: collectstatic failed"
    touch /openimis-be/.init_done
  fi
}

#export PYTHONPATH="/opt/app:$PYTHONPATH"
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  export DJANGO_SETTINGS_MODULE=openIMIS.settings
fi

case "$1" in
  "start" )
    init
    echo "Starting Django..."
    python server.py
  ;;
  "start_asgi" )
    init
    echo "Starting Django ASGI..."
    def_ip='0.0.0.0'
    def_port='8000'
    def_app='openIMIS.asgi:application'

    SERVER_IP="${ASGI_IP:-$def_ip}"
    SERVER_PORT="${ASGI_PORT:-$def_port}"
    SERVER_APPLICATION="${ASGI_APPLICATION:-$def_app}"

    daphne -b "$SERVER_IP" -p "$SERVER_PORT" "$SERVER_APPLICATION"
  ;;
  "start_wsgi" )
    init
    echo "Starting Django WSGI..."
    def_ip='0.0.0.0'
    def_port='8000'
    def_app='openIMIS.wsgi'

    SERVER_IP="${WSGI_IP:-$def_ip}"
    SERVER_PORT="${WSGI_PORT:-$def_port}"
    SERVER_APPLICATION="${WSGI_APPLICATION:-$def_app}"
    SERVER_WORKERS="${WSGI_WORKERS:-4}"

    gunicorn -b "$SERVER_IP:$SERVER_PORT" -w $SERVER_WORKERS "$SERVER_APPLICATION"
  ;;
  "worker" )
    echo "Starting Celery with url ${CELERY_BROKER_URL} ${DB_NAME}..."
    echo "Settings module: $DJANGO_SETTINGS_MODULE"
    celery -A openIMIS worker --loglevel=DEBUG
  ;;
  "manage" )
    ./manage.py "${@:2}"
  ;;
  "eval" )
    eval "${@:2}"
  ;;
  "bash" )
    bash
  ;;
  * )
    show_help
  ;;
esac
