#!/bin/bash
# Run the gunicorn service

# Make sure we're in the right virtual env and location
source /home/paul/.virtualenvs/pwc/bin/activate
source /home/paul/.virtualenvs/pwc/bin/postactivate

cd /home/paul/pwc

exec gunicorn -c /home/paul/pwc/_site_setup/gunicorn.conf.py pwc.wsgi:application