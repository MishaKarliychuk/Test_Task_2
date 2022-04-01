"""Выполнены задачи 1-го пункта (А, B, C, D)"""

import string
import random
import mysql.connector
from pymongo import MongoClient

from services import read_csv, create_csv


symbols = string.ascii_uppercase + string.digits + string.ascii_lowercase

COUNT_ROWS = 1024 # К-во записей
LENGTH_RANDOM = 8  # Длина рандомной строки
USER_MYSQL = "root"  # Пароль к MySQL
PASSWOR_MYSQL = "PASSWORD"  # Пароль к MySQL


def Task_A():
    headers = ['1', '2', '3', '4', '5', '6']
    data_rows = []

    def ran_word():
        return ''.join(random.choices(symbols, k=LENGTH_RANDOM))

    for i in range(COUNT_ROWS):
        data_rows.append([ran_word(), ran_word(), ran_word(), ran_word(), ran_word(), ran_word()])

    create_csv("A.csv", headers, data_rows)

def Task_B():
    headers = ['1', '2', '3', '4', '5', '6']
    VOWELS = 'aeiouAEIOU'

    data_rows = read_csv("A.csv")
    new_data_rows = []

    for row in data_rows:
        new_row = []
        add_to_data_rows = True
        for item in row:
            # Если гласная буква
            if item[0] in VOWELS:
                add_to_data_rows = False
                break

            new_item = item

            for symbol in item:
                # Если не четное число
                if symbol.isdigit():
                    if int(symbol)%2 != 0:
                        new_item = new_item.replace(symbol, "#")

            new_row.append(new_item)

        if add_to_data_rows:
            new_data_rows.append(new_row)

    create_csv("B.csv", headers, new_data_rows)

def Task_c():
    ####

    db = mysql.connector.connect(
        host="localhost",
        user=USER_MYSQL,
        password=PASSWOR_MYSQL
    )
    with db.cursor() as cur:
        cur.execute("CREATE DATABASE IF NOT EXISTS testDB;")
    db.close()

    ####

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=PASSWOR_MYSQL,
        database="testDB"
    )

    with mydb.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS test;")
        cur.execute("CREATE TABLE test (row_1 VARCHAR (8), row_2 VARCHAR (8), row_3 VARCHAR (8), row_4 VARCHAR (8), row_5 VARCHAR (8), row_6 VARCHAR (8));")


    data_rows = read_csv("A.csv")

    with mydb.cursor() as cur:
        sql = "INSERT INTO test (row_1, row_2, row_3, row_4, row_5, row_6) VALUES (%s, %s, %s, %s, %s, %s);"
        for row in data_rows:
            cur.execute(sql, (row[0], row[1], row[2], row[3], row[4], row[5]))
        mydb.commit()

    with mydb.cursor() as cur:
        cur.execute("DELETE FROM test WHERE row_2 REGEXP '^[0-9]';")
        mydb.commit()

    mydb.close()

def Task_D():
    data_rows = read_csv("A.csv")

    client = MongoClient('localhost', 27017)
    current_db = client['testDB']

    collection = current_db['test']
    collection.delete_many({"row_1": {"$regex": "^"}})

    data_to_insert = []
    for row in data_rows:
        data_to_insert.append({
            "row_1": row[0],
            "row_2": row[1],
            "row_3": row[2],
            "row_4": row[3],
            "row_5": row[4],
            "row_6": row[5],
        })

    collection.insert_many(data_to_insert)
    collection.delete_many({"row_3": {"$regex": "^[a-zA-Z]"}})

if __name__ == '__main__':
    Task_A()
    Task_B()
    Task_c()
    Task_D()
