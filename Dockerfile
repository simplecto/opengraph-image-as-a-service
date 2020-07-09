#FROM python:3.6-slim
FROM ubuntu:18.04 

RUN apt-get update && \
    apt-get install -y git python3-pip firefox-geckodriver chromium-chromedriver && \
    apt-get autoremove

COPY requirements.txt /
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r /requirements.txt
RUN mkdir /app
COPY src/ app/

RUN ln -s /usr/bin/python3 /usr/bin/python

ARG RELEASE
ENV RELEASE ${RELEASE}

ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8000

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]
