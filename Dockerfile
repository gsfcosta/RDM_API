FROM python:slim-buster

WORKDIR /flask-app

COPY requirements.txt requirements.txt
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /flask-app

COPY . .

ENV FLASK_APP=app.py
USER root
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["-m", "gunicorn", "-b", "0.0.0.0:80", "app:app"]