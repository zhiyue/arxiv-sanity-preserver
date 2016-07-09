import sqlite3
conn = sqlite3.connect('as.db')



cursor = conn.cursor()
cursor.execute('drop table if exists user')
cursor.execute(
'''create table user (
  user_id integer primary key autoincrement,
  username text not null,
  pw_hash text not null,
  creation_time integer
)''')

cursor.execute('drop table if exists library')
cursor.execute(
'''create table library (
  lib_id integer primary key autoincrement,
  paper_id text not null,
  user_id integer not null,
  update_time integer
)''')

conn.commit()
conn.close()


