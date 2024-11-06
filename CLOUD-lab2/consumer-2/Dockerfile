FROM python:3.8-slim

WORKDIR /app

COPY consumer.py /app

RUN pip install azure-eventhub azure-storage-file-datalake azure-identity aiohttp azure-storage-blob azure-storage-file-datalake

CMD ["python", "consumer.py"]
