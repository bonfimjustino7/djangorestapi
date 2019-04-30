# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.context import Context

from threading import Thread
from time import sleep
from util.models import EmailAgendado


def sendmail(subject='', to=[], params={}, template='', mimetype='text/html; charset=UTF-8', headers={}):
    # from .models import Recurso
    # ativo = Recurso.objects.get_or_create(recurso='EMAIL')[0].ativo
    headers.update({'Reply-To': settings.REPLY_TO_EMAIL, })
    '''
    Método para envio de e-mail:
    - subject: string contendo assunto do e-mail
    - to: lista dos e-mails dos destinatários
    - params: dicionário com os parâmetros para renderizar o e-mail
    - template: string para o caminho do template do e-mail
    - mimetype: string de tipo e charset do arquivo de e-mail, padrão 'text/html; charset=UTF-8'
    '''
    def send_thread_email(assunto='', to=[], params={}, template='', mimetype='', headers={}):

        email = EmailAgendado.objects.create(
            subject=assunto,
            to=','.join(to)
        )

        text_content = assunto
        try:
            template_content = get_template(template)
            html_content = template_content.render(params)
            email.html = html_content
            tentativas = 0
        except Exception as e:
            email.html = u'%s' % e
            tentativa = 4
        email.save()

        while tentativas < 3:
            try:
                if settings.SEND_EMAIL:
                    msg = EmailMultiAlternatives(assunto, text_content, settings.DEFAULT_FROM_EMAIL, bcc=to, headers=headers)
                    msg.attach_alternative(email.html, mimetype)
                    msg.send()
                    email.status = 'K'
                    email.save()
                    break
                else:
                    email.status = 'A'
                    email.save()
                    break
            except:
                tentativas += 1
                if tentativas < 3:
                    email.status = 'R'
                else:
                    email.status = 'E'
                email.save()
                sleep(60)

    th = Thread(target=send_thread_email, args=(subject, to, params, template, mimetype, headers))
    th.start()
