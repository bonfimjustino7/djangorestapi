from django.apps import AppConfig

import requests
from bs4 import BeautifulSoup


class InscricaoConfig(AppConfig):
    name = 'inscricao'


def valida_youtube(url):
    url = url.split('//')
    try:
        url = url[1].split('www.')[1]
        host = url.split('/')[0]

    except:
        url = url[0].split('www.')[1]
        host = url.split('/')[0]

    if not 'youtube.com' == host and not 'youtu.be' == host and not 'vimeo.com' == host:
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