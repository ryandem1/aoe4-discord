import contextlib
import os

import psycopg2
import psycopg2.extras
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


def write_relics(*relics: aoe4_discord.models.RelicRow) -> None:
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
            data = [
                (
                    f'{relic["game_id"]}{relic["name"]}',
                    relic["game_id"],
                    relic["name"],
                    relic["winner"],
                    relic["score"]
                )
                for relic in relics
            ]
            cursor.executemany(insert_query, data)
            connection.commit()
            logger.info("Relics inserted successfully.")
        except psycopg2.Error as e:
            connection.rollback()
            logger.error(f"Error inserting relics: {e}")
        finally:
            cursor.close()


def write_games(*games: aoe4_discord.models.GameRow) -> None:
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


def read_relic_stats(relic_name: str) -> aoe4_discord.models.RelicStats:
    """Reads relic stats by name."""
    query = """
    SELECT
        MAX(score) AS MAX_SCORE,
        (
        SELECT winner
        FROM relics
        WHERE name = %s
        AND score = (
            SELECT MAX(score)
            FROM relics
            WHERE name = %s
        )
        ) AS MAX_SCORE_PLAYER,
        (
        SELECT winner
        FROM relics
        WHERE name = %s
        GROUP BY winner
        ORDER BY COUNT(*) DESC
        LIMIT 1
        ) AS MAX_RELICS_PLAYER,
        (
        SELECT COUNT(*) AS NUM_RELICS
        FROM relics
        WHERE name = %s
        GROUP BY winner
        ORDER BY NUM_RELICS DESC
        LIMIT 1
        ) AS MAX_RELICS
    FROM relics
    WHERE name = %s;
    """
    with pg_connection() as connection:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query, vars=[relic_name] * 5)  # need to insert the relic name 5 times

        rows = cursor.fetchall()
        stats = next(
            aoe4_discord.models.RelicStats(
                name=relic_name,
                max_score=row["max_score"],
                max_score_player=row["max_score_player"],
                most_relics=row["max_relics"],
                most_relics_player=row["max_relics_player"],
            )
            for row in rows
        )
        cursor.close()

    return stats
