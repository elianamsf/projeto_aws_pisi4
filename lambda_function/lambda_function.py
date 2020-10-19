import json
import requests
import datetime
import boto3
from botocore.config import Config
import uuid

inputStream = "INMET_STREAM"
kinesis = 'kinesis'
   
def get_data_api():
    now  = datetime.datetime.now()
    date = now.date()
    date = str(date)
    url  = 'https://apitempo.inmet.gov.br/estacao/dados/'+date
    resp = requests.get(url)
    json_j = resp.json()
    lista_pe = {}
    lista_pe =[ elemento for elemento in json_j if elemento['UF'] == 'PE']
    saida = lista_pe
    return saida

def create_client():
    client = boto3.client(kinesis)
    return client

def send_to_kinesis(client, data):
    send= []
    key   = str(uuid.uuid1())
    for element in data:
        dic = {}
        CD_ESTACAO = element['CD_ESTACAO']
        TEM_INS = element['TEM_INS']
        UMD_INS = element['UMD_INS']
        if TEM_INS is not None:
            TEM_INS = 1.8* float(TEM_INS) + 32
        dic['TEM_INS'] = TEM_INS
        dic['UMD_INS'] = UMD_INS
        dic['CD_ESTACAO'] = CD_ESTACAO
        dic = json.dumps(dic)
        record = bytes(dic,'utf-8')
        response = {
            'Data':record,
            'PartitionKey':key
        }
        send.append(response)
    result =  client.put_records(StreamName=inputStream, Records=send)
    return result
    
def lambda_handler(event, context):
    data = get_data_api()
    kinesis = create_client()
    retorno = send_to_kinesis(kinesis, data)
    return retorno
    
