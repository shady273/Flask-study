import math
import re
import sqlite3
import time

from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Error read DB" + str(e))
        return []

    def add_post(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Стаття з таким URL уже існує")
                return False

            base = url_for('static', filename='images')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>", text)

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Error add to DB" + str(e))
            return False

        return True

    def get_post(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE  '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res

        except sqlite3.Error as e:
            print("Error get post from DB " + str(e))

        return False, False

    def get_post_anonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Error get posts from DB' + str(e))

        return []

    def add_user(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Користувач з таким email уже зареєстрований")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка при додаванні в DB " + str(e))
            return False
        return True

    def get_user(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайдений")
                return False

            return res
        except sqlite3.Error as e:
            print("Помилка отримання даниз DB " + str(e))

        return False

    def get_user_by_email(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Користувач не знайдений')
                return False

            return res
        except sqlite3.Error as e:
            print("Помилка отримання даних з DB " + str(e))

        return False

    def updata_user_avatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка оновлення аватарки в DB: "+str(e))
            return False
        return True
