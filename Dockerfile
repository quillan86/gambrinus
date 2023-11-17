# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker/64642121#64642121
# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker/64642121#64642121
# https://stackoverflow.com/questions/70793654/how-can-i-make-packages-installed-using-poetry-accessible-in-docker
# https://github.com/orgs/python-poetry/discussions/1879
FROM python:3.10-slim as base

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="$PATH:/runtime/bin:/opt/mssql-tools18/bin" \
  PYTHONPATH="$PYTHONPATH:/runtime/lib/python3.10/site-packages" \
  # Versions:
  POETRY_VERSION=1.4.2 \
  HF_DATASETS_OFFLINE=1 \
  ACCEPT_EULA=Y

FROM base AS builder

# System deps:
# https://github.com/mkleehammer/pyodbc/wiki/Install#installing-on-linux
# https://towardsdatascience.com/deploying-python-script-to-docker-container-and-connect-to-external-sql-server-in-10-minutes-225ff4c19ce5
RUN apt-get update \
 && apt-get -y install gcc g++ unzip wget \
 && apt-get -y install curl gnupg gnupg2 apt-utils \
 && apt-get -y install locales apt-transport-https \
 && apt-get -y install --reinstall build-essential

# poetry
RUN pip install "poetry==$POETRY_VERSION"
WORKDIR /src

# Generate requirements and install *all* dependencies.
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install --prefix=/runtime --force-reinstall -r requirements.txt

COPY /app ./app

FROM base AS final

COPY --from=builder /runtime /usr/local

# SQL Server Driver
# https://stackoverflow.com/questions/71414579/how-to-install-msodbcsql-in-debian-based-dockerfile-with-an-apple-silicon-host
RUN apt-get update \
    && apt-get install -y --no-install-recommends apt-utils gnupg curl gcc g++ apt-transport-https build-essential \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && ACCEPT_EULA=Y apt-get -y install mssql-tools18 \
    && apt-get install -y --no-install-recommends unixodbc-dev tdsodbc

# CONFIGURE ENV FOR /bin/bash TO USE MSODBCSQL18
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc


WORKDIR /src
COPY gunicorn.conf.py ./
COPY /app ./app

EXPOSE 3100

CMD ["gunicorn", "app.main:app", "--timeout", "90"]