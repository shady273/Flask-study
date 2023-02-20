from flask import Flask, render_template, request, flash, session, redirect, url_for, abort, g, make_response
from FDataBase import FDataBase
import _sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required
from UserLogin import UserLogin

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'dfsfhlwnsdofhoewhfvsodsfvxk'

app = Flask(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.secret_key = SECRET_KEY

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().from_db(user_id, dbase)


def connect_db():
    conn = _sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = _sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.get_menu(), posts=dbase.get_post_anonce())


@app.route("/add_post", methods=["POST", "GET"])
def add_post():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.add_post(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash("Помилка додавання статті", category='error')
            else:
                flash("Стаття добавлена", category='success')
        else:
            flash("Помилка додавання статті", category='error')

    return render_template('add_post.html', menu=dbase.get_menu(), title='Додавання статті')


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    title, post = dbase.get_post(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.get_menu(), title=title, post=post)


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == "POST":
        print(request.form)
        if len(request.form["username"]) > 2:
            flash('Повідомлення відправлено', category='success')
        else:
            flash('Помилка відправки', category='error')

    return render_template('feedback.html', title="Зворотній звʼязок")


@app.route("/profile/<username>")
def profile(username):
    if "userLogged" not in session or session["userLogged"] != username:
        abort(401)
    return f"Профіль користувача {username}"


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.get_user_by_email(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect(url_for('index'))

        flash("Неправильний логін або пароль", category="error")

    return render_template("login.html", menu=dbase.get_menu(), title="Авторизація")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["email"]) > 4 \
                and len(request.form["psw"]) > 4 and request.form["psw"] == request.form["psw2"]:
            hash = generate_password_hash(request.form["psw"])
            res = dbase.add_user(request.form["name"], request.form["email"], hash)
            if res:
                flash("Ви успішно зереєструвались", category='success')
                return redirect(url_for('login'))
            else:
                flash("Помилка при додаванні в DB", category='error')
        else:
            flash("Неправельно заповнені поля", category='error')

    return render_template("register.html", menu=dbase.get_menu(), title="Реєстрація")


@app.route("/logout")
def logout():
    pass


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', menu=dbase.get_menu(), title='Сторінка не знайдена'), 404


@app.errorhandler(401)
def page_not_found(error):
    return render_template('page404.html', menu=dbase.get_menu(), title='Необхідно авторизуватись'), 401


if __name__ == "__main__":
    app.run(debug=True)