from flask import Flask, render_template, request, flash, session, redirect, url_for, abort, g, make_response
from FDataBase import FDataBase
import _sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'dfsfhlwnsdofhoewhfvsodsfvxk'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.secret_key = SECRET_KEY
app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Щоб переглянути цю сторінку необхідно авторизуватись'
login_manager.login_message_category = 'success'


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


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", menu=dbase.get_menu(), title="Профіль")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.get_user_by_email(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            user_login = UserLogin().create(user)
            rm = form.remember.data
            login_user(user_login, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash("Неправильний логін або пароль", category="error")

    return render_template("login.html", menu=dbase.get_menu(), title="Авторизація", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(form.psw.data)
            res = dbase.add_user(form.name.data, form.email.data, hash)
            if res:
                flash("Ви успішно зереєструвались", category='success')
                return redirect(url_for('login'))
            else:
                flash("Помилка при додаванні в DB", category='error')

    return render_template("register.html", menu=dbase.get_menu(), title="Реєстрація", form=form)


@app.route('/userava')
@login_required
def userava():
    img = current_user.get_avatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file and current_user.verify_ext(file.filename):
            try:
                img = file.read()
                res = dbase.updata_user_avatar(img, current_user.get_id())
                if not res:
                    flash("Помилка оновлення аватарки", "error")
                flash("Аватар оновлено", 'success')
            except FileNotFoundError as e:
                flash("Помилка читання файла", 'error')
        else:
            flash("Помилка оновлення аватарки", "error")

    return redirect(url_for('profile'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з акаунту", category='success')
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', menu=dbase.get_menu(), title='Сторінка не знайдена'), 404


if __name__ == "__main__":
    app.run(debug=True)
