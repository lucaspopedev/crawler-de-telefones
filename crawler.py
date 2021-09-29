import re
import threading

import requests
from bs4 import BeautifulSoup


URL_AUTOMOVEIS = 'https://django-anuncios.solyd.com.br'

LINKS = []

TELEFONES = []


def requisicao_get(url):
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            return resposta.text
        else:
            print('Erro ao fazer requisição')
    except Exception as e:
        print('Erro ao fazer requisição: {}'.format(e))


def parsing(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html, 'html.parser')
        return soup
    except Exception as e:
        print('Erro ao fazer parsing HTML: {}'.format(e))


def encontrar_links(soup):
    try:
        cards_pai = soup.find('div', class_='ui three doubling link cards')
        cards = cards_pai.find_all('a')
        links = []

        for card in cards:
            try:
                link = card['href']
                links.append(link)
            except:
                pass
        
        return links
    
    except Exception as e:
        print('Erro ao encontrar links: {}'.format(e))
        return None


def encontrar_telefones(soup):
    try:
        descricao = soup.find_all('div', class_='sixteen wide column')[2].p.get_text().strip()
    except Exception as e:
        print('Errro ao encontrar descrição: {}'.format(e))
        return None
    
    regex_de_telefone = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.]?\d{4})[ \-\.]?(\d{4})", descricao)

    if regex_de_telefone:
        return regex_de_telefone


def descobrir_telefones():
    while True:
        try:
            link_anuncio = LINKS.pop(0)
        except:
            break

        resposta_anuncio = requisicao_get(URL_AUTOMOVEIS + link_anuncio)

        if resposta_anuncio:
            soup_anuncio = parsing(resposta_anuncio)
            if soup_anuncio:
                telefones = encontrar_telefones(soup_anuncio)
                if telefones:
                    for telefone in telefones:
                        print('Telefone encontrado: {}'.format(telefone))
                        TELEFONES.append(telefone)
                        salvar_telefones(telefone)
                        


def salvar_telefones(telefone):

    string_telefone = '({}) {}-{}\n'.format(telefone[0], telefone[1], telefone[2])

    try:
        with open('telefones.csv', 'a') as arquivo:
            arquivo.write(str(string_telefone))
    except Exception as e:
        print('Erro ao salvar arquivo: {}'.format(e))


if __name__ == "__main__":
    resposta_busca = requisicao_get(URL_AUTOMOVEIS)
    if resposta_busca:
        soup_busca = parsing(resposta_busca)
        if soup_busca:
            LINKS = encontrar_links(soup_busca)

            THREADS = []

            # Instância das threads que vão executar a função descobrir_telefones
            for i in range(5):
                t = threading.Thread(target=descobrir_telefones)
                THREADS.append(t)

            # Iniciando as threads
            for t in THREADS:
                t.start()
            
            # Espera da finalização das threads
            for t in THREADS:
                t.join()

            print('Os telefones foram salvos no arquivo telefones.csv!')