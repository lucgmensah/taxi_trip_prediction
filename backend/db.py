import sqlite3
from sqlite3 import Error
from typing import Optional


def create_connection(db_file: str):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def create_table(conn):
    try:
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS trip_predict (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hour INTEGER NOT NULL,
            abnormal_period INTEGER NOT NULL,
            weekday INTEGER NOT NULL,
            month INTEGER NOT NULL,
            prediction FLOAT NOT NULL
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
    except Error as e:
        print(e)



def insert_prediction(conn, hour: int, abnormal_period: int, weekday: int, month: int, prediction: float):
    try:
        sql_insert = """
        INSERT INTO trip_predict (hour, abnormal_period, weekday, month, prediction)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor = conn.cursor()
        cursor.execute(sql_insert, (hour, abnormal_period, weekday, month, prediction))
        conn.commit()
        return cursor.lastrowid  # Return the ID of the last inserted record
    except Error as e:
        print(e)


def get_all_predictions(conn):
    try:
        sql_select = "SELECT * FROM trip_predict;"
        cursor = conn.cursor()
        cursor.execute(sql_select)
        return cursor.fetchall()
    except Error as e:
        print(e)
