FROM python:3.12

WORKDIR /bot

COPY . .
RUN pip install .

CMD ["sh", "-c", "aoe4_discord/server.py &"]
CMD ["python", "aoe4_discord/main.py"]
