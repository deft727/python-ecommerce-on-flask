
import os
basedir = os.path.abspath(os.path.dirname(__file__))
class MConfig :

    SECRET_KEY = '3254365h6k5g6kh7k5kjlhr5h4ouirhhh324'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER =  'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True 
    MAIL_USERNAME = 'zarj09'
    MAIL_PASSWORD = 'Kirill99121'

    MY_KEY = 1234
    SUPERUSER = 'root'
    PICS_FOLDER = "/static/images"
    