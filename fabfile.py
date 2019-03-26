from __future__ import with_statement
from fabric.contrib import console 
from fabric.api import *

@with_settings(warn_only=True)
@hosts("webapp@107.170.161.189")
def deploy_test():
    with cd('/var/webapp/colunistas/colunistas/'):
        run('git pull')
        run('../bin/python manage.py migrate --settings=colunistas.settings.test')
        run('../bin/python manage.py collectstatic --noinput --settings=colunistas.settings.test')
        run('supervisorctl restart colunistas')

