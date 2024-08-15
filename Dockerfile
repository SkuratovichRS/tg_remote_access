FROM python:3.10.14

WORKDIR /workdir

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY *.py .
COPY app app



