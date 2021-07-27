FROM python:3.8-slim-buster
WORKDIR /backend
COPY ./backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY ./Docker/backend/wsgi* ./start/
COPY ./data/data.json ./
COPY ./backend/ ./
