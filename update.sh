#!/bin/sh
LOCAL_PATH="/var/webapp/colunistas/colunistas"
cd ${LOCAL_DB_PATH}
git pull
../bin/python manage.py collectstatic --no-input
supervisorctl restart colunistas
