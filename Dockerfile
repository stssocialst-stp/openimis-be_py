FROM python:3.11-bullseye As builder
ENV PYTHONUNBUFFERED 1
ARG DB_DEFAULT
## No need to update sources.list for bullseye
RUN apt-get update \
 && apt-get install -y apt-transport-https ca-certificates gettext unixodbc-dev \
 && apt-get upgrade -y

RUN apt-get install -y -f python3-dev
RUN apt-get -y install git

RUN test "$DB_DEFAULT" != "postgresql" && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - || :
RUN test "$DB_DEFAULT" != "postgresql" && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list || :
RUN test "$DB_DEFAULT" != "postgresql" && apt-get update || :
RUN test "$DB_DEFAULT" != "postgresql" && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools || :

RUN pip install --upgrade pip
RUN test "$DB_DEFAULT" != "postgresql" && pip install mssql-cli || :

RUN pip install gunicorn

FROM builder As app

# Install requirements
COPY requirements.txt /.
RUN pip install -r requirements.txt

ARG SENTRY_DSN
RUN test -z "$SENTRY_DSN" || pip install -r sentry-requirements.txt && :

RUN mkdir /openimis-be
COPY . /openimis-be
WORKDIR /openimis-be

ARG OPENIMIS_CONF_JSON
ENV OPENIMIS_CONF_JSON=${OPENIMIS_CONF_JSON:-openimis.json}
WORKDIR /openimis-be/script
RUN python modules-requirements.py ../${OPENIMIS_CONF_JSON} > modules-requirements.txt && pip install -r modules-requirements.txt
WORKDIR /openimis-be/openIMIS

# Note: compilemessages and collectstatic moved to entrypoint.sh to avoid scheduler issues

ENTRYPOINT ["/openimis-be/script/entrypoint.sh"]
