# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

openIMIS backend is a modular Django-based health insurance management system built with a GraphQL API. The system uses a modular plugin architecture where functionality is distributed across independent Python packages that are dynamically loaded from `openimis.json`.

## Architecture

### Modular Plugin System

The core architectural principle is **modularity**. Each feature (claim, policy, insuree, etc.) is a separate Python package that can be:
- Installed from PyPI
- Loaded from local directories (editable install with `pip install -e`)
- Pulled from git repositories

Modules are configured in `openimis.json` which lists:
- Module names
- Installation sources (pip package, git URL, or local path)

The system dynamically:
1. Loads all modules listed in `openimis.json` via `openIMIS/openIMIS/openimisapps.py`
2. Discovers and aggregates GraphQL schemas from each module's `schema.py`
3. Combines all module queries and mutations into a single GraphQL endpoint
4. Binds signals across modules via `signal_binding` (always loaded last)

### Key Files

- `openimis.json` - Module registry and configuration
- `openIMIS/openIMIS/settings.py` - Django settings with extensive env var configuration
- `openIMIS/openIMIS/schema.py` - GraphQL schema aggregator that dynamically imports all module schemas
- `openIMIS/openIMIS/openimisapps.py` - Module discovery and loading logic
- `openIMIS/openIMIS/openimisconf.py` - Configuration loader
- `.env` - Environment configuration (copy from `.env.example`)

### Database Support

Supports both PostgreSQL and MS SQL Server:
- Database engine configured via `DB_DEFAULT` env var (`postgresql` or `mssql`)
- PostgreSQL requires `postgres-json-schema` extension
- MS SQL requires ODBC Driver 17
- Database routing configured in `openIMIS/openIMIS/routers.py`

### GraphQL API

All data access is through GraphQL (not REST, except FHIR module):
- Single endpoint at `/api/graphql` (if `SITE_ROOT=api`)
- Schema dynamically built from all modules
- Pagination uses Relay cursor-based pattern
- Authentication via JWT (Bearer token)
- Rate limiting configured via `RATELIMIT_*` env vars
- See `GraphQL.md` for detailed API usage

### Background Jobs

- Uses APScheduler with Django integration
- Jobs stored in database via `django-apscheduler`
- Celery available for async tasks (requires RabbitMQ)
- Scheduled tasks configured in `settings.py` `SCHEDULER_JOBS` array
- Auto-start controlled by `SCHEDULER_AUTOSTART` env var

### Security

Production mode (`MODE=PROD`) enables:
- CSRF protection (configure `CSRF_TRUSTED_ORIGINS`)
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- JWT RSA signing (place keys in `openIMIS/keys/`)
- Account lockout mechanism via django-axes
- Password complexity requirements
- Rate limiting on GraphQL endpoint

## Development Commands

### Initial Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate module requirements from openimis.json
python script/modules-requirements.py openimis.json > modules-requirements.txt

# Install all openIMIS modules
pip install -r modules-requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations (from openIMIS/ directory)
cd openIMIS
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
python manage.py changepassword <username>

# Start development server
python manage.py runserver
```

### Testing

```bash
# Run tests for specific module (keeps test database)
python manage.py test --keep <module_name>

# Run tests for all modules
python script/modules-tests.py

# Initialize test database (if needed)
python init_test_db.py
```

### Module Development

```bash
# Create new module skeleton
python manage.py create_openimis_module <module_name> <author> <email> [--template business|calculation] [--github]

# Install existing module locally (editable)
python manage.py install_module_locally <module_name> [--url <git_url>] [--branch <branch>] [--path <dir>]

# Install all modules locally
python manage.py install_module_locally all

# Install module from PyPI
python manage.py install_module_pypi <module_name> [--target-version <version>]

# Create calculation rule module
python manage.py create_calcrule_module <module_name> <author> <email> [--github]
```

### Working with Modules

To modify an existing module:
1. Clone module repo next to (not inside) `openimis-be_py/`
2. Uninstall packaged version: `pip uninstall openimis-be-<module>`
3. Install local version: `pip install -e ../openimis-be-<module>_py/`
4. Changes are now live-reloaded

Module structure requirements:
- Must have `urls.py` with `urlpatterns = []` (even if empty)
- Must be registered in `openimis.json`
- Should have `schema.py` with `Query` and/or `Mutation` classes for GraphQL

### Translation Management

```bash
# Extract translations from module
cd <module_root>
../openimis-be_py/script/gettext.sh

# Compile messages (from openIMIS/)
python manage.py compilemessages -x zh_Hans

# Extract frontend translations
python manage.py extract_translations
```

### Profiling (DEV mode only)

Add query parameters to any endpoint:
- `prof=True` - Get profiler report
- `download=True` - Format for snakeviz

Example: `http://localhost:8000/api/graphql?prof=True&download=True`

### Release Management

```bash
# Create release branches for all modules
python manage.py create_release_branch <version> [<from_branch>]

# Generate current openimis.json snapshot
python script/generate-current-json.py
```

## Docker Commands

```bash
# Build Docker image
docker build . -t openimis-be-<version> [--build-arg DB_DEFAULT=postgresql]

# Run with environment file
docker run --env-file .env openimis-be-<version>

# Use docker-compose
docker-compose up
```

Container entrypoint commands (via `script/entrypoint.sh`):
- `start` - Start Django with `python server.py`
- `start_asgi` - Start with Daphne (WebSocket support)
- `start_wsgi` - Start with Gunicorn (production)
- `worker` - Start Celery worker
- `manage <args>` - Run Django management commands
- `bash` - Interactive shell

## Important Development Notes

### Environment Variables

The system is heavily configured via environment variables. Key variables:
- `MODE` - `DEV` or `PROD` (affects debug, async behavior, security)
- `DB_DEFAULT` - `postgresql` or `mssql`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database connection
- `SITE_ROOT` - URL prefix (e.g., `api` makes endpoints at `/api/...`)
- `SECRET_KEY` - Django secret (required in production)
- `OPENIMIS_CONF_JSON` - Path to custom openimis.json
- `ROW_SECURITY` - Enable data filtering by user rights (default: True)

See `.env.example` for complete list with descriptions.

### Custom Exception Handlers

REST-based modules can register custom exception handlers in their `apps.py`:

```python
from openIMIS.ExceptionHandlerRegistry import ExceptionHandlerRegistry
from .exceptions.handler import my_handler

class MyModuleConfig(AppConfig):
    def ready(self):
        ExceptionHandlerRegistry.register_exception_handler(MODULE_NAME, my_handler)
```

### OpenSearch Integration

Modules can use OpenSearch for advanced reporting:
- Configure via `OPENSEARCH_HOST`, `OPENSEARCH_ADMIN`, `OPENSEARCH_PASSWORD`
- Load existing data: `python manage.py add_<model>_data_to_opensearch`
- See `openimis-be-opensearch_reports_py` module for details

### Using openimis-be-core Features

When developing modules, leverage features from `openimis-be-core`:
- Date handling utilities
- User info context
- Base models and mixins
- Common GraphQL types
- Authentication backends

### Developer Tools Module

The `developer_tools` module provides management commands for:
- Creating module skeletons
- Installing modules locally or from PyPI
- Adding GitHub CI workflows
- Managing translations
- Creating release branches

## Common Issues

### Wheel Package Errors

If `pip install -r requirements.txt` fails with wheel errors:
```bash
pip install wheel
python setup.py bdist_wheel
# If still failing on Ubuntu/Debian:
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools
apt-get install -y python3-dev unixodbc-dev
pip install --upgrade pip
```

### PostgreSQL Setup

Requires `postgres-json-schema` extension:
```bash
git clone https://github.com/gavinwahl/postgres-json-schema
# Follow installation in that repo

# Create database
psql postgres -c 'create database coremis'

# Initialize schema
git clone https://github.com/openimis/database_postgresql
cd database_postgresql
bash concatenate_files.sh
psql -d coremis -a -f output/fullDemoDatabase.sql

# Then run migrations
python manage.py migrate
```

### Wrong Database Docker Version

Use recommended database docker build commands from the [openimis-db_dkr repository](https://github.com/openimis/openimis-db_dkr).

## Module-Specific Notes

### Current Installation (from openimis.json)

Most modules install from `release/25.04` branch, except:
- `individual` - from `dpssf-stp/openimis-be-individual_py@stp-changes`
- `payroll` - from `dpssf-stp/openimis-be-payroll_py@stp-changes`
- `grievance_social_protection` - from `dpssf-stp/openimis-be-grievance_social_protection_py@stp-changes`
- `claim_sampling` - from `develop` branch
- `api_etl` - from `develop` branch

These custom branches may have deployment-specific customizations.

## PEP+ Module Integration

### Overview

**PEP+ (Programa de Educação Positiva)** is a custom extension module integrated directly into this repository. It manages educational sessions for family groups with the following tools:

- **Ferramenta 1**: Session Planning (SessaoPEP)
- **Ferramenta 2**: Attendance Registration (PresencaSessao)
- **Ferramenta 3**: Session Execution (ExecucaoSessao)
- **Ferramenta 4**: Session Supervision (SupervisaoSessao)
- **Ferramenta 5**: District Bimonthly Reports (RelatorioDistritalBimestral)

### Architecture Integration

PEP+ is **NOT** in `openimis.json` but loads automatically in development via conditional logic:

**Directory Structure:**
```
openimis-be_py/
├── openimis-be-pep_plus_py/    # PEP+ module (part of this repo)
│   ├── pep_plus/
│   │   ├── models.py           # 8 core models
│   │   ├── schema.py           # GraphQL schema
│   │   ├── gql_queries.py      # Query definitions
│   │   ├── gql_mutations.py    # Mutation definitions
│   │   ├── services.py         # Business logic
│   │   ├── admin.py            # Django admin registration
│   │   └── validators.py       # Data validation
│   ├── API_DOCUMENTATION.md    # Complete GraphQL API docs
│   └── VALIDATION_REPORT.md    # Technology compatibility report
├── openIMIS/
├── script/
└── docker-compose-dev.yml
```

**Auto-Loading Mechanism:**

PEP+ loads automatically in development via three integration points:

1. **openIMIS/openIMIS/openimisapps.py** (line ~140):
```python
def openimis_apps():
    OPENIMIS_CONF = load_openimis_conf()
    apps = [*map(extract_app, OPENIMIS_CONF["modules"])]

    # Add PEP+ module dynamically if it exists (for development)
    if os.path.exists('/app/openimis-be-pep_plus_py') and 'pep_plus' not in apps:
        apps.append('pep_plus')

    return apps
```

2. **openIMIS/openIMIS/settings.py** (line ~380):
```python
# Add PEP+ module for development (module is installed via entrypoint.sh)
if os.path.exists('/app/openimis-be-pep_plus_py') and 'pep_plus' not in INSTALLED_APPS:
    try:
        signal_binding_index = INSTALLED_APPS.index('signal_binding')
        INSTALLED_APPS.insert(signal_binding_index, 'pep_plus')
        OPENIMIS_APPS.append('pep_plus')
    except ValueError:
        INSTALLED_APPS.append('pep_plus')
        OPENIMIS_APPS.append('pep_plus')
```

3. **script/entrypoint.sh** (line ~100):
```bash
# Install PEP+ module if it exists (for development)
if [ -d "/app/openimis-be-pep_plus_py" ]; then
  echo "Installing PEP+ module..."
  pip install -e /app/openimis-be-pep_plus_py
fi
```

This approach ensures:
- ✅ PEP+ loads only when directory exists (backwards compatible)
- ✅ Works in development without modifying `openimis.json`
- ✅ Doesn't affect production deployments without PEP+
- ✅ Changes are live-reloaded via editable install

### Technology Stack

PEP+ follows **100% openIMIS patterns** (validated in `VALIDATION_REPORT.md`):

- **Base Classes**: `VersionedModel`, `BaseService`, `OpenIMISMutation`
- **GraphQL**: `graphene-django` with `ExtendedConnection`, `OrderedDjangoFilterConnectionField`
- **Pagination**: Relay cursor-based pattern
- **Filtering**: Django Filter with custom operators
- **Validation**: Service layer with Django validators
- **Permissions**: Same permission system as other modules
- **Audit**: `audit_user_id` for all operations
- **Transactions**: `transaction.atomic()` for data integrity

### Development with PEP+

**Docker Compose Setup:**

The `docker-compose-dev.yml` mounts PEP+ for live development:

```yaml
backend:
  volumes:
    - ./openimis-be-pep_plus_py:/app/openimis-be-pep_plus_py
    - ./openIMIS/file_storage:/app/file_storage
    - ./openIMIS/staticfiles:/app/staticfiles
```

**Starting Development Environment:**

```bash
# Start all services
docker-compose -f docker-compose-dev.yml up --build

# Backend will automatically:
# 1. Install PEP+ in editable mode (pip install -e)
# 2. Run migrations for PEP+ models
# 3. Load PEP+ GraphQL schema
# 4. Register PEP+ in Django admin
```

**Accessing PEP+ Features:**

1. **Django Admin Panel**: `http://localhost:8000/admin/`
   - Navigate to "PEP_PLUS" section
   - Full CRUD interface for all 8 models
   - Filter, search, and export capabilities

2. **GraphQL API**: `http://localhost:8000/api/graphql`
   - See `openimis-be-pep_plus_py/API_DOCUMENTATION.md` for complete documentation
   - 31 operations across 8 entities
   - Full query/mutation examples with filters and pagination

### PEP+ Models

All models extend `VersionedModel` for soft delete and audit tracking:

1. **ModuloEducacional** - Educational modules with ordering and duration
2. **GrupoFamiliar** - Family groups linked to Individual (from individual module)
3. **SessaoPEP** - Planned sessions with module, location, and facilitator
4. **PresencaSessao** - Attendance records with states (presente/faltou/justificado)
5. **ExecucaoSessao** - Session execution with topics, observations, materials
6. **SupervisaoSessao** - Session supervision with ratings and feedback
7. **RelatorioDistritalBimestral** - Bimonthly district reports with indicators
8. **EncaminhamentoSessao** - Session referrals with types and states

### Changes to Main Project

PEP+ integration required minimal changes to the main project (all validated in `ALTERACOES_PROJETO_PRINCIPAL.md`):

**Bug Fixes (benefit entire project):**
1. **Locale Paths Deduplication** (`openimisapps.py`): Fixed RecursionError by removing 779 duplicate locale paths
2. **SCHEDULER_AUTOSTART Fix** (`settings.py`): Fixed boolean environment variable parsing
3. **Build Performance** (`Dockerfile`): Moved `compilemessages` to runtime to avoid scheduler conflicts

**Conditional PEP+ Loading:**
4. Auto-detection in `openimisapps.py`
5. Auto-loading in `settings.py`
6. Auto-install in `entrypoint.sh`
7. Volume mount in `docker-compose-dev.yml`

**Result**: Zero breaking changes, all modifications are backwards compatible.

### API Documentation

Complete GraphQL API documentation for frontend teams is available at:
- **Location**: `openimis-be-pep_plus_py/API_DOCUMENTATION.md`
- **Format**: Swagger-like documentation with TypeScript types
- **Coverage**: All 31 operations (queries + mutations)
- **Examples**: Complete workflow examples with pagination and filtering

### Testing PEP+

**Django Admin Testing:**
```bash
# 1. Start containers
docker-compose -f docker-compose-dev.yml up

# 2. Create superuser (if not exists)
docker exec -it openimis-backend python manage.py createsuperuser

# 3. Access admin panel
# Navigate to: http://localhost:8000/admin/
# Login with superuser credentials
# Go to "PEP_PLUS" section
```

**GraphQL Testing:**
```bash
# Query educational modules
curl -X POST http://localhost:8000/api/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "{ modulosEducacionais { edges { node { codigo nome } } } }"
  }'
```

### Production Deployment

To deploy PEP+ in production:

1. **Option A - Add to openimis.json** (recommended):
```json
{
  "name": "pep_plus",
  "pip": "openimis-be-pep_plus"
}
```

2. **Option B - Keep conditional loading**:
   - Ensure `openimis-be-pep_plus_py/` directory exists in deployment
   - Auto-loading will activate automatically

3. **Run migrations**:
```bash
python manage.py migrate pep_plus
```

### Known Issues

**RecursionError in Admin (FIXED)**:
- **Symptom**: Django admin crashes with "maximum recursion depth exceeded"
- **Cause**: Duplicate locale paths (779 duplicates out of 800 total)
- **Fix**: Deduplication logic in `openimisapps.py:get_locale_folders()`
- **Status**: ✅ Resolved permanently

**JWT Authentication**:
- **Symptom**: GraphQL authentication may fail with "User has no attribute private_key"
- **Workaround**: Use Django Admin panel for testing (no JWT required)
- **Status**: ⚠️ Admin panel provides full functionality

### Maintenance Notes

**When modifying PEP+:**
- Changes to `.py` files are live-reloaded (editable install)
- Model changes require migrations: `docker exec -it openimis-backend python manage.py makemigrations pep_plus`
- Schema changes are automatically detected by GraphQL introspection
- Admin changes require container restart

**When updating main project:**
- PEP+ conditional loading is safe - won't activate if directory missing
- All changes tested with and without PEP+ present
- Technology compatibility validated in `VALIDATION_REPORT.md` (90% score)
