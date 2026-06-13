# Kode patch untuk kerentanan yang ditemukan
# Misalnya, perbaikan untuk vulnerability SQL Injection
import mysql.connector

def execute_query(query, params):
    cnx = mysql.connector.connect(
        user='username',
        password='password',
        host='127.0.0.1',
        database='database'
    )
    cursor = cnx.cursor()
    cursor.execute(query, params)
    cnx.commit()
    cursor.close()
    cnx.close()
