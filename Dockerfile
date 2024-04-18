FROM python:3.12

WORKDIR /bot

COPY . .
RUN pip install .
