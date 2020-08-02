import sqlite3

# service.dbとつなぐ(なければ作られる)
conn = sqlite3.connect('service.db')
c = conn.cursor()

# テーブル作成
c.execute("create table user(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)")
c.execute("create table bbs(id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER, comment TEXT)")


# 確定
conn.commit()

# バイバイ
conn.close()
