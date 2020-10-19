"""

aws emr add-steps --cluster-id j-23EEAM3NN5CQN --steps Type=Spark,Name="Kinesis-SQL",ActionOnFailure=CONTINUE,Args=[--jars,s3://sparkkinesis/spark-sql-kinesis_2.11-1.2.1_spark-2.4-SNAPSHOT.jar,s3://sparkkinesis/kinesis_example.py,kinesis-sql,pyspark-kinesis,https://kinesis.us-east-1.amazonaws.com,us-east-1]

"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, Row
import boto3
import requests

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: kinesis_example.py <app-name> <stream-name> <endpoint-url> <region-name>")
        sys.exit(-1)

    applicationName, streamName, endpointUrl, regionName = sys.argv[1:]

    spark = SparkSession \
        .builder \
        .appName(applicationName) \
        .getOrCreate()

    kinesis = spark \
        .readStream \
        .format('kinesis') \
        .option('streamName', streamName) \
        .option('endpointUrl', endpointUrl)\
        .option('region', regionName) \
        .option('startingposition', 'LATEST')\
        .load()\

    schema = StructType([
        StructField("TEM_INS", StringType()),
        StructField("UMD_INS", StringType()),
        StructField("CD_ESTACAO", StringType())])
    
    tb_host = "demo.thingsboard.io"
    device_token = "ywiqs7jCfXlkxp0yxTTH"

    def send_data_to_tb(data):
        try:
            url = 'http://' + tb_host + '/api/v1/' + device_token + '/telemetry'
            requests.post(url, json=data)
        except ConnectionError:
            print('Failed to send data.')

    def process(row):
        #print("Oie! :D")
        data = row.asDict()
        t = data["TEM_INS"]
        u = data["UMD_INS"]
        cod = data["CD_ESTACAO"]
        hi = 0.0
        if t is not None and u is not None:
            temperatura = float(t)
            umidade = float(u)
            hi_pre = 1.1*temperatura - 10.3 + 0.047 * umidade
            if hi_pre < 80:
                hi = hi_pre
            else:
                hi_pre_two = (-42.379 + 2.04901523 * temperatura + 10.4333127 * umidade - 0.22475541 * temperatura * umidade
                            - 0.00683783 * temperatura**2 - (5.481717*(10**-2)) * umidade**2 + (1.22874*(10**-3)) *
                            temperatura**2*umidade +
                            (8.5282*(10**-4)) * temperatura *
                            umidade**2 - (1.99*(10**-6))
                            * temperatura**2 * umidade**2)
                if (80 <= temperatura and temperatura <= 112) and umidade <= 13:
                    hi_pre_three = hi_pre_two - \
                        (3.25-0.25*umidade) * ((17-abs(temperatura - 95))/17)**0.5
                    hi = hi_pre_three
                else:
                    if (80 <= temperatura and temperatura <= 87) and umidade > 85:
                        hi_pre_four = hi_pre_two + 0.02 * \
                            (umidade-85)*(87-temperatura)
                        hi = hi_pre_four
                    else:
                        hi = hi_pre_two
        tempc = (hi - 32)/1.8
        #print(tempc)
        nivel_alerta = ''
        if tempc <= 27.0:
            nivel_alerta = 'Normal'
        elif (tempc >= 27.1) and (tempc <=32.0):
            nivel_alerta = 'Cautela'
        elif (tempc >= 32.1) and (tempc <=41.0):
            nivel_alerta = 'Cautela Extrema'
        elif (tempc >= 41.1) and (tempc <=54.0):
            nivel_alerta = 'Perigo'
        elif tempc > 54:
            nivel_alerta = 'Perigo Extrema'
        hi_str = str(tempc)
        nivel_alerta_str = str(nivel_alerta),
        cod_str = str(cod)
        data = {'temperatura':hi_str,'nivel_alerta': nivel_alerta_str, 'cod_estacao': cod_str}
        send_data_to_tb(data) 

        #clientSQS = boto3.client('sqs', region_name='us-east-1')
        #url = "https://sqs.us-east-1.amazonaws.com/589020551826/fila-sqs-inmet"
        #clientSQS.send_message(QueueUrl=url, MessageBody=str(row))

    kinesis\
        .selectExpr('CAST(data AS STRING)')\
        .select(from_json('data', schema).alias('data'))\
        .select('data.*')\
        .writeStream\
        .outputMode('append')\
        .foreach(process)\
        .trigger(processingTime='2 seconds') \
        .start()\
        .awaitTermination()
