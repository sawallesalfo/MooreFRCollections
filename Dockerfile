# Use the official Python image from the Docker Hub
FROM python:3.12-slim

USER root

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*


RUN pip install git+https://github.com/openai/whisper.git 

