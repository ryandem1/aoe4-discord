import contextlib
import os

import psycopg2
import logging

import aoe4_discord.models

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


def write_relics_to_db(*relics: aoe4_discord.models.RelicRow) -> None:
    """Will write one or more relic objects to the RELICS table

    :param relics: list[aoe4_discord.models.RelicRow]
    :return: None
    """
    insert_query = """
        INSERT INTO RELICS (ID, GAME_ID, NAME, WINNER, SCORE)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ID) DO NOTHING;
    """
    with pg_connection() as connection:
        cursor = connection.cursor()
        try:
            data = [(f'{relic["game_id"]}{relic["name"]}', relic["game_id"], relic["name"], relic["winner"], relic["score"]) for relic in relics]
            cursor.executemany(insert_query, data)
            connection.commit()
            logger.info("Relics inserted successfully.")
        except psycopg2.Error as e:
            connection.rollback()
            logger.error(f"Error inserting relics: {e}")
        finally:
            cursor.close()


def write_games_to_db(*games: aoe4_discord.models.GameRow) -> None:
    """Will write one or more game objects to the GAMES table

    :param games: list[aoe4_discord.models.GameRow]
    :return: None
    """
    insert_query = """
        INSERT INTO GAMES (ID, MAP, OUTCOME, END_REASON, DURATION, GAME_MODE, PLAYERS)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ID) DO NOTHING;
    """
    with pg_connection() as connection:
        cursor = connection.cursor()
        try:
            data = [
                (
                    game["id"],
                    game["map"],
                    game["outcome"],
                    game["end_reason"],
                    game["duration"],
                    game["game_mode"],
                    game["players"]
                )
                for game in games
            ]
            cursor.executemany(insert_query, data)
            connection.commit()
            logger.info("Games inserted successfully.")
        except psycopg2.Error as e:
            connection.rollback()
            logger.error(f"Error inserting games: {e}")
        finally:
            cursor.close()

