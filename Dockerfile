FROM python:3.10-alpine

WORKDIR /code

ENV FLASK_APP=api.py

ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4000

COPY . .

CMD python init_api.py