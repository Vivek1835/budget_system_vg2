# db.py - everything that talks to the database is here.
# The database password is NOT written in the code. It comes from the .env file.

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    # Open a connection to MariaDB.
    # DictCursor means every row comes back as a dictionary, like row["name"].
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "budget_app"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "smartbudget"),
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
