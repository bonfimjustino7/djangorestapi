#!/bin/sh
LOCAL_PATH="/var/webapp/colunistas/"
${LOCAL_DB_PATH}/bin/python ${LOCAL_DB_PATH}/colunistas/manage.py collectstatic --no-input
supervisorctl restart colunistas
