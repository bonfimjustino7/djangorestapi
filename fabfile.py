from __future__ import with_statement
from fabric.contrib import console 
from fabric.api import *

@with_settings(warn_only=True)
@hosts("webapp@colunistas.irdx.com.br:2222")
def deploy_test():
    with cd('/var/webapp/colunistas/colunistas/'):
        run('git pull')
        run('../bin/python manage.py migrate')
        run('../bin/python manage.py collectstatic')
        run('supervisorctl restart colunistas')


@with_settings(warn_only=True)
@hosts("desenv1@35.184.116.225:2222")
def deploy_alumni():
    with cd('/var/webapp/ongportal/ongportal/'):
        run('git pull')
        # if console.confirm("Install requirements.txt?", default=False):
        #    run('../bin/pip install -r requirements.txt')
        if console.confirm("Run migrations?", default=False):
            run('../bin/python manage.py migrate')
        if console.confirm("Run collectstatic?", default=False):
            run('../bin/python manage.py collectstatic --no-input')
        run('supervisorctl restart ongportal')