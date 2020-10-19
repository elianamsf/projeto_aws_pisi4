# Roteiro: Apresentação Projeto Final

## Projeto Interdisciplinar para Sistemas de Informação IV

# Pré-requisitos

- [ ]  Região e formato como json e us-uest-1, respectivamente no ~.aws/config
- [ ]  Credencias AWS atualizadas em ~.aws/credentials,
- [ ]  Função Lambda criada com o gatilho configurado no Cron
- [ ]  Stream no Kinesis ativo
- [ ]  [Opcional] Fila ativa no SQS
- [ ]  Cluster executando uma 1 etapa que lê os dados do Kinesis, faz a conta e envia o resultado para o DashBoard no ThingsBoard e para a fila no SQS.
- [ ]  Liberar o acesso SSH na porta 22 das instâncias EC2 do Master e Workers do Cluster.
- [ ]  As instâncias EC2 do Master e Workers do Cluster devem ter as bibliotecas
boto3 e requests instaladas.
- [ ]  Código com a conta e envio pra ThingsBoards e SQS no Bucket S3.

# Roteiro

- [ ]  Enviar o código com a com a conta e envio pra ThingsBoard e SQS para Bucket S3.
- [ ]  Criar um Cluster com 1 Master e 2 Workers.
- [ ]  Liberar acesso SSH para meu IP no grupo de segurança nas instâncias EC2.
- [ ]  Instalar as bibliotecas python  boto3 e requests nas instâncias.

```bash
$ pip install boto3
```

```bash
$ pip install requests
```

- [ ]  Copiar o ID do Cluster e enviar o step via console no para o Cluster.

```bash
aws emr add-steps --cluster-id j-2QOXNSK2ZY9I2 --steps Type=Spark,Name="Kinesis Queue",ActionOnFailure=CONTINUE,Args=[--jars,s3://inmet-data/spark-sql-kinesis_2.11-1.2.1_spark-2.4-SNAPSHOT.jar,s3://inmet-data/kinesis_example.py,kinesis-sql,INMET_STREAM,https://kinesis.us-east-1.amazonaws.com,us-east-1]
```

![Roteiro%20Apresentac%CC%A7a%CC%83o%20Projeto%20Final%2039537abccfd94dedab61c29968b72c20/Untitled.png](Roteiro%20Apresentac%CC%A7a%CC%83o%20Projeto%20Final%2039537abccfd94dedab61c29968b72c20/Untitled.png)

- [ ]  Verificar se o cluster está executando com sucesso.
- [ ]  Ativar o gatilho do Lambda no Cron.

- [ ]  Verificar se dados estão indo pra o Stream no Kinesis Data Stream.
- [ ]  Verificar se os dados estão chegando na fila do SQS.
- [ ]  Verificar se os dados estão sendo exibidos no Dashboard no ThingsBoard

[ThingsBoard Demo](https://demo.thingsboard.io/dashboard/8c622990-0ef2-11eb-a50a-7fed1f51b550?publicId=b3613c00-1197-11eb-af98-19366df12767)