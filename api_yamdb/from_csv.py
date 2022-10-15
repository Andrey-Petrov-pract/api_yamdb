import csv
import sqlite3

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/category.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['name'], i['slug']) for i in dr]
cur.executemany("INSERT INTO reviews_category (id, name, slug)"
                " VALUES (?, ?, ?);", to_db)
con.commit()
con.close()

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/genre.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['name'], i['slug']) for i in dr]
cur.executemany("INSERT INTO reviews_genre (id, name, slug)"
                " VALUES (?, ?, ?);", to_db)
con.commit()
con.close()

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/genre_title.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['title_id'], i['genre_id']) for i in dr]
cur.executemany("INSERT INTO reviews_genretitle (id, title_id, genre_id)"
                " VALUES (?, ?, ?);", to_db)
con.commit()
con.close()

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/titles.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['name'], i['year'], i['category']) for i in dr]
cur.executemany("INSERT INTO reviews_title (id, name, year, category_id)"
                " VALUES (?, ?, ?, ?);", to_db)
con.commit()
con.close()

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/review.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['title_id'], i['text'], i['author'], i['score'],
              i['pub_date']) for i in dr]
cur.executemany("INSERT INTO reviews_review (id, title_id, text, author_id,"
                " score, pub_date) VALUES (?, ?, ?, ?, ?, ?);", to_db)
con.commit()
con.close()

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/comments.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['review_id'], i['text'],
              i['author'], i['pub_date']) for i in dr]
cur.executemany("INSERT INTO reviews_comment (id, review_id, text, author_id,"
                " pub_date) VALUES (?, ?, ?, ?, ?);", to_db)
con.commit()
con.close()

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
with open('api_yamdb/static/data/users.csv', 'r', encoding="utf8") as f:
    dr = csv.DictReader(f, delimiter=",")
    to_db = [(i['id'], i['username'], i['email'], i['role'], i['bio'],
              i['first_name'], i['last_name']) for i in dr]
cur.executemany("INSERT INTO reviews_user (id, username, email, role, bio,"
                " first_name, last_name, password, is_superuser, is_staff,"
                " is_active, date_joined, confirmation_code)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, 'xxx', 'false', 'false',"
                " 'True', '2022-10-10T14:50:30.010155Z', 'no code');", to_db)
con.commit()
con.close()
