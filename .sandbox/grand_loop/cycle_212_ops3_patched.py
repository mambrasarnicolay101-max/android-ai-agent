# Tidak ada kode sistem asli yang disediakan, 
# namun sebagai contoh, kita akan melakukan patch pada kerentanan SQL Injection
# pada kode berikut:
# 
# def proses_request(request):
#     query = "SELECT * FROM users WHERE username = '" + request['username'] + "' AND password = '" + request['password'] + "'"
#     cursor.execute(query)
#     return cursor.fetchall()

# Patch:
import sqlalchemy as db

engine = db.create_engine('mysql://user:password@localhost/dbname')
connection = engine.connect()

def proses_request(request):
    query = db.select([db.table('users')]).where(db.and_(db.table('users').c.username == request['username'], db.table('users').c.password == request['password']))
    result = connection.execute(query)
    return result.fetchall()
