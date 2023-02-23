from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, DataRequired, Length


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email()])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField("Запамятати", default=False)
    submit = SubmitField("Увійти")