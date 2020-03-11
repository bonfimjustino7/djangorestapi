from django.apps import AppConfig

import requests
from bs4 import BeautifulSoup


class InscricaoConfig(AppConfig):
    name = 'inscricao'


def valida_youtube(url):
    url = url.split('//')
    if 'www' in url[1]:
        url = url[1].split('.')
        url = url[1] + '.' + url[2]
    else:
        url = url[1]
    url = url.split('/')[0]
    if not 'youtube.com' == url and not 'youtu.be' == url and not 'vimeo.com' == url:
        return 'O filme ou vídeo deve estar hospedado no YouTube ou no Vimeo!'

    r = requests.get('http://' + url)
    if not r.ok:
        return 'Link %s inválido. Vídeo não encontrado.' % url
    else:
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.title.text
        if title == 'YouTube':
            return 'Link inválido. O vídeo não existe no servidor especificado.'


    return