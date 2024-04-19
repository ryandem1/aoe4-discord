FROM python:3.12

# Set environment variables
ENV PORT=8080
ENV APP_HOME /app

WORKDIR /$APP_HOME

COPY . .
RUN pip install .

CMD ["sh", "-c", "aoe4_discord/server.py &"]
CMD ["python", "aoe4_discord/main.py"]
