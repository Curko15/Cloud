FROM python:3.8-slim

WORKDIR /app

COPY consumer.py /app

RUN pip install requests azure-eventhub azure-eventhub-checkpointstoreblob-aio

CMD ["python", "consumer.py"]
