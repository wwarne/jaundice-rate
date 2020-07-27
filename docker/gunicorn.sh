#!/usr/bin/env sh

set -o errexit
set -o nounset

# We are using `gunicorn` for production, see:
# http://docs.gunicorn.org/en/stable/configure.html


# Start gunicorn with 4 workers:
/usr/local/bin/gunicorn server:gunicorn_app_factory \
  --worker-class aiohttp.GunicornWebWorker \
  --workers=4 `# Sync worker settings` \
  --timeout=30 `# timeout for worker (default = 30) \
  --bind='0.0.0.0:8080' `# Run aiohttp on 8080 port` \
  --chdir='/code'       `# Locations` \
  --log-file=- \
  --worker-tmp-dir='/dev/shm'
