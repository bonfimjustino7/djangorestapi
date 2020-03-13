from django.apps import AppConfig

import requests
from bs4 import BeautifulSoup


class InscricaoConfig(AppConfig):
    name = 'inscricao'


def valida_youtube(url):
    url = url.split('://')
    try:
        if len(url) > 1 and url[1].startswith('www.'):
            url = url[1].replace('www.', '')
        else:
            url = url[1]
        host = url.split('/')[0]
    except:
        host = ''

    if host != 'youtube.com' and not host != 'youtu.be' and host != 'vimeo.com':
        return 'O filme ou vídeo deve estar hospedado no YouTube ou no Vimeo!'

    r = requests.get('http://' + url)
    if not r.ok:
        return 'Link %s inválido. Vídeo não encontrado.' % url
    else:
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.title.text
        if title == 'YouTube':
            return 'Link inválido. O vídeo não existe no servidor especificado.'
