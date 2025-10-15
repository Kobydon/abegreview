from enum import unique
from flask import Flask,render_template ,request,url_for,flash,redirect,g,Response,jsonify


from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import  DateTime
from sqlalchemy.sql import func

from functools import wraps
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.sqltypes import LargeBinary
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# from flask_wtf import FlaskForm,RecaptchaField
# from wtforms import StringField,PasswordField
# from wtforms.validators import InputRequired,Length
from flask_marshmallow import Marshmallow
from flask_restful import Api,Resource, marshal,reqparse,abort,fields,marshal_with
from flask_cors import CORS, cross_origin
import flask_praetorian
import tempfile

import base64


from werkzeug.utils import secure_filename

from flask_mail import Mail, Message
from flask_migrate import Migrate
#from flask_script import Manager



