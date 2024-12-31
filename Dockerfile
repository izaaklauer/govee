FROM python:3.12-alpine3.18

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /app
WORKDIR /app

CMD ["python", "main.py"]

