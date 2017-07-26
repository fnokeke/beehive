#!/bin/bash

WORKERS=4
WORKER_CLASS="sync"
PORT=5000

~/.virtualenvs/rep-aws-env/bin/gunicorn \
--bind 0.0.0.0:${PORT} \
-w ${WORKERS} -k ${WORKER_CLASS} \
--reload wsgi:app --access-logfile logs/access.log --error-logfile logs/error.log
