FROM python:3.8-slim

WORKDIR /app

COPY producer.py /app

RUN pip install requests azure-eventhub

CMD ["python", "producer.py"]
