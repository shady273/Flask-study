from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):
    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return self.__user['name'] if self.__user else "Без Імені"

    def get_email(self):
        return self.__user['email'] if self.__user else "Без Email"

    def get_avatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/avatar.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не знайдений аватар по замовчуванню: " + str(e))
        else:
            img = self.__user['avatar']

        return img

    def verify_ext(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == 'png' or ext == "PNG":
            return True
        return False
