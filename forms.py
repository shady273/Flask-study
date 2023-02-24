from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некоректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100,
                                                               message="Пароль повинен бути не коротше 3 символів")])
    remember = BooleanField("Запамятати", default=False)
    submit = SubmitField("Увійти")


class RegisterForm(FlaskForm):
    name = StringField("Ім'я: ", validators=[Length(min=3, max=100, message="Ім'я повинно містити мінімум 3 символи")])
    email = StringField("Email: ", validators=[Email("Некоректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100,
                                                               message="Пароль повинен бути не коротше 3 символів")])
    psw2 = PasswordField("Повторити пароль: ", validators=[DataRequired(), EqualTo('psw',
                                                                                 message="Паролі не співпадають")])
    submit = SubmitField("Реєстрація")