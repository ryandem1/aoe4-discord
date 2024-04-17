FROM python:3.12

WORKDIR /bot

COPY . .
RUN pip install .

CMD ["python", "aoe4_discord/main.py"]