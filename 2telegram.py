# coding: utf-8
from datetime import datetime, timedelta
import requests
import os
import csv

# Lista dos ativos a serem monitorados
ativos = ["petr4", "goll4","abev3","itsa4"]

# Arquivo que guarda os ultimos precos enviados
filename = "ultimos-precos.csv"

# Variacao que ativa o envio da msg
PORCENTAGEM = 0.015

# Token do bot do telegram (Jean)
TOKEN_TELEGRAM = "TOKEN_QUE_O_BOTHFATHER_TE_DEU"

# Nome do canal que serao enviadas as mensagens
CHANNEL_NAME = "@NOME_DO_CANAL_QUE_VC_CRIOU"

# Curl que vai ser usado no 'send_msg', caso for rodar em servidor com proxy tem que setar nele
CURL_COMMAND = "curl -vk "

# Usa a api do telegram pra enviar a msg
def send_msg(msg):
	url = "\'https://api.telegram.org/bot"+TOKEN_TELEGRAM+"/sendMessage?parse_mode=markdown&chat_id="+CHANNEL_NAME+"&text="+msg+"\'"
	curl = CURL_COMMAND+url
	os.system(curl)

def get_csv(filename):
	with open(filename, 'rb') as csvfile:
		reader = csv.reader(open(filename))
		result = {}
		for row in reader:
		    key = row[0]
		    if key in result:
		        pass
		    result[key] = row[1:]
	return result

def texto_em_negrito(string_text):
	return "*"+string_text+"*"

# Cria um novo arquivo. Params: str(nome_do_arquivo), str(conteudo)
def criar_arquivo(nome_do_arquivo, conteudo):
	with open(nome_do_arquivo, "wb") as f:
		f.write(conteudo)

# Vai no yahoo e pega um json cheio de informacoes, estou usando soh preco, nome e hora
def get_dados_yahoo(ativo):
	dic = {}
	url = "https://query1.finance.yahoo.com/v8/finance/chart/"+ativo+".SA?symbol=AZUL4.SA&period1=1542074400&period2=1566788400&interval=1d&includePrePost=true&events=div%7Csplit%7Cearn&lang=pt-BR&region=BR&crumb=nboaxOK9xPx&corsDomain=br.financas.yahoo.com"
	s = requests.Session()
	dados = s.get(url)
	dados_json = dados.json()

	nome = ativo
	preco = dados_json['chart']['result'][0]['meta']['regularMarketPrice']
	tempo = dados_json['chart']['result'][0]['meta']['regularMarketTime']

	dic[nome] = [preco, tempo]
	return dic

def get_preco(dados):
    return str(dados.values()[0][0])

def get_nome(dados):
	return str(dados.keys()[0])

def get_time(dados):
    return str(dados.values()[0][1])

# Converte um timestamp unix p/ timestamp
def get_date_from_timestamp(unix_int_timestamp):
    ts = int(unix_int_timestamp)
    date = datetime.utcfromtimestamp(ts) - timedelta(hours=3)

    return date.strftime('%d-%m-%Y %H:%M:%S')

# Prita um resumo das acoes
def resumo(ibov_list):
	msg = ""
	valores = []
	for ativo in ibov_list:
		result = get_dados_yahoo(ativo)
		nome = get_nome(result)
		preco = get_preco(result)
		tempo = get_time(result)
		msg = msg+nome+","+preco+","+tempo+"\n"
	return msg


def valores(lista_ativos):
    for ativo in lista_ativos:
        result = get_dados_yahoo(ativo[0])
        nome = get_nome(result)
        preco = get_preco(result)
        tempo = get_time(result)
        data = get_date_from_timestamp(tempo)
        print preco

def verifica_alertas(dict_enviado):
	alertas = []
	for ativo in dict_enviado:
		valor_enviado = float(dict_enviado[ativo][0])

		dados = get_dados_yahoo(ativo)
		valor_agora = dados[ativo][0]

		subiu = valor_enviado + valor_enviado*PORCENTAGEM
		desceu = valor_enviado - valor_enviado*PORCENTAGEM
		
		if valor_agora > subiu or valor_agora < desceu:
			alertas.append(ativo)
	return alertas

def dict_2_string(dicionario):
	str1 = ""
	for x in dicionario:
		str1 = str1 + x + "," +','.join(str(e) for e in dicionario[x])+'\n'
	return str1

def atualiza_dict(alerta, dicionario):
	dados = get_dados_yahoo(alerta)
	dicionario[alerta] = dados[alerta]
	return dicionario

def notify_me(alertas):
	for x in alertas:
		preco_antigo = float(meus_precos[x][0])
		lista_enviada = atualiza_dict(x, meus_precos)
		preco_novo = float(lista_enviada[x][0])
		str1 = dict_2_string(lista_enviada)

		if preco_novo > preco_antigo:
			send_msg(x+" **UP**"+" "+str(preco_antigo)+" -> "+str(preco_novo))
		else:
			send_msg(x+" **DOWN**"+" "+str(preco_antigo)+" -> "+str(preco_novo))
	
	criar_arquivo(filename, str1)

#############################################################################################

# Cria o arquivo inicial com os valores, caso nao exista:
if not os.path.isfile(filename):
	precos = resumo(ativos)
	criar_arquivo(filename, precos)

# Lê o arquivo com os preços: 
meus_precos = get_csv(filename)

# Verifica se algum ativo variou mais que a PORCENTAGEM
alertas = verifica_alertas(meus_precos)

# Se houver alertas, vai enviar a msg pro telegram
if alertas:
	notify_me(alertas)