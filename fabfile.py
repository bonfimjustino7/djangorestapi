from __future__ import with_statement
from fabric.contrib import console 
from fabric.api import *

@with_settings(warn_only=True)
@hosts("webapp@colunistas.irdx.com.br:2222")
def deploy_test():
    with cd('/var/webapp/colunistas/colunistas/'):
        run('git pull')
        run('../bin/python manage.py migrate')
        run('../bin/python manage.py collectstatic --no-input')
        run('supervisorctl restart colunistas')
