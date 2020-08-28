FROM python:3.7.7-slim-buster AS development_build

LABEL maintainer="wwarne@gmail.com"

ARG BUILD_ENV

ENV BUILD_ENV=${BUILD_ENV} \
  # python
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.0.10 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

# Installing `poetry` package manager:
# https://github.com/python-poetry/poetry
RUN pip install "poetry==$POETRY_VERSION" && poetry --version

# Copy only requirements, to cache them in docker layer:
WORKDIR /code
COPY ./poetry.lock ./pyproject.toml /code/

# Project initialization:
RUN set -ex \
  && apt-get update \
  # we might need to install some package that needs to compile some C code.
  && buildDeps=" \
       build-essential \
    " \
  && apt-get install -y $buildDeps --no-install-recommends \
  && echo "$BUILD_ENV" \
  && poetry install \
    $(if [ "$BUILD_ENV" = 'production' ]; then echo '--no-dev'; fi) \
    --no-interaction --no-ansi \
  # Cleaning poetry installation's cache for production:
  && apt-get purge -y --auto-remove $buildDeps \
  && apt-get clean && rm -rf /var/lib/apt/lists/* \
  && if [ "$BUILD_ENV" = 'production' ]; then rm -rf "$POETRY_CACHE_DIR"; fi

# To not forget our port
EXPOSE 8080

CMD [ "/usr/local/bin/gunicorn", \
      "server:gunicorn_app_factory", \
      "--worker-class=aiohttp.GunicornWebWorker", \
      "--workers=4", \
      "--timeout=30", \
      "--bind=0.0.0.0:8080", \
      "--chdir=/code", \
      "--log-file=-", \
      "--worker-tmp-dir=/dev/shm" \
]

# copy source code inside the image only for prod images.
# for dev images we will mount project directory into image
FROM development_build AS production_build

COPY . /code
