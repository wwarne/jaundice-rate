FROM python:3.7.7-slim-buster

LABEL maintainer="wwarne@gmail.com"

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # tini:
  TINI_VERSION=v0.19.0 \
  # poetry:
  POETRY_VERSION=1.0.9 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
     wget \
  # Installing `tini` utility:
  # https://github.com/krallin/tini
  && wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini" \
  && chmod +x /usr/local/bin/tini && tini --version \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && pip install "poetry==$POETRY_VERSION" && poetry --version

# Copy only requirements, to cache them in docker layer:
WORKDIR /code
COPY ./poetry.lock ./pyproject.toml /code/

# Project initialization:
RUN set -ex \
  && poetry install --no-dev --no-interaction --no-ansi \
  && rm -rf "$POETRY_CACHE_DIR"


# This is a special case. We need to run this script as an entry point:
COPY ./docker/aio_app/gunicorn.sh /docker-gunicorn.sh
# Setting up proper permissions:
RUN chmod +x '/docker-gunicorn.sh' \
  && groupadd -r web && useradd -d /code -r -g web web \
  && chown web:web -R /code

# Running as non-root user:
USER web
# To not forget our port
EXPOSE 8080

# We customize how our app is loaded with the custom entrypoint:
ENTRYPOINT ["tini", "--"]
CMD ["sh", "/docker-gunicorn.sh"]

COPY --chown=web:web . /code
