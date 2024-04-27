import contextlib
import os

import psycopg2
import logging

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def pg_connection():
    """Establishes a PG connection to use"""
    database = os.environ["PG_DATABASE"]
    username = os.environ["PG_USERNAME"]
    password = os.environ["PG_PASSWORD"]
    host = os.environ["PG_HOST"]
    port = os.environ["PG_PORT"]

    connection = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=host,
        port=port
    )
    logger.info(f"connected to pg {database} at {host}:{port} using db {database}")

    yield connection

    connection.close()
