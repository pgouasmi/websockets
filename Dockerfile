FROM python:3

RUN apt-get update && apt-get upgrade -y

WORKDIR /usr/src/app

COPY sources ./sources

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/sources

RUN pwd

CMD ["python3", "app.py"]