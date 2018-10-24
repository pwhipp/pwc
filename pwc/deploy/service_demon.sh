#!/bin/bash
# Run the django runserver on port 8000

# Make sure we're in the right virtual env and location
source /home/paul/.virtualenvs/pwc/bin/activate
source /home/paul/.virtualenvs/pwc/bin/postactivate

cd /home/paul/pwc

exec django-admin.py runserver 0.0.0.0:8100