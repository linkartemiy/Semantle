FROM python:3.11
WORKDIR /semantle

COPY requirements.txt requirements.txt
COPY .env .env

RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python3", "main.py"]
