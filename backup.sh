#!/bin/sh
DB_NAME="ongportal_test"
DB_USERNAME="ongportal"
DB_PASSWORD="logica38"
DATE=`date +%Y%m%d`

LOCAL_DB_PATH="/var/webapp/ongportal_test/backups"
S3_DB_PATH="s3://ongportal/db"

# Mysql backup
mysqldump -u $DB_USERNAME -p${DB_PASSWORD} $DB_NAME | gzip > ${LOCAL_DB_PATH}/${DB_NAME}_backup_${DATE}.gz

#Copy db to S3
/usr/local/bin/aws s3 sync ${LOCAL_DB_PATH} ${S3_DB_PATH}