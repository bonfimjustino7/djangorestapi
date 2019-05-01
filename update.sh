#!/bin/bash
cd /var/webapp/colunistas/colunistas
git pull
../bin/python manage.py collectstatic --no-input
supervisorctl restart colunistas
