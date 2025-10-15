from application.extensions import *

class LoginForm(FlaskForm):
    #username = StringField('username ',validators=[InputRequired('username is required')])
    #password = PasswordField('password')
    recaptcha = RecaptchaField()