from  application.extensions import *
from  application.settings import *
from  application.extensions.extensions import Flask,SQLAlchemy
app = Flask(__name__)

app.app_context().push()