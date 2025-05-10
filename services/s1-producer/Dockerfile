FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY schema.md producer.py ./
CMD ["python", "producer.py"]
