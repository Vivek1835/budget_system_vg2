# db.py - everything that talks to the database is here.
# The database address and password are NOT written in the code.
# They come from the .env file.

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    # Open a connection to the database.
    # DictCursor means every row comes back as a dictionary, like row["name"].

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "budget_app")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "smartbudget")
    ca_file = os.getenv("DB_SSL_CA", "")

    if ca_file != "":
        # An online database (like TiDB Cloud) needs an encrypted connection.
        # ca_file is the file that lets us check that the server is the real one.
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
            ssl_ca=ca_file,
            ssl_verify_cert=True,
            ssl_verify_identity=True,
        )
    else:
        # A database on the same computer (localhost) needs no encryption.
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
        )

    return connection


def get_rows(sql, values=()):
    # Run a SELECT. Returns a list of rows.
    # The %s signs in the sql are filled in safely from "values".
    # This is what stops SQL injection.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_one(sql, values=()):
    # Run a SELECT and return only the first row.
    # If there is no row, return None.
    rows = get_rows(sql, values)
    if len(rows) > 0:
        return rows[0]
    return None


def run_command(sql, values=()):
    # Run an INSERT, UPDATE or DELETE and save the change.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, values)
    connection.commit()
    connection.close()
    