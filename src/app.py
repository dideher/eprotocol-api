# app.py
from flask import Flask
#from flask_cors import CORS
from extensions import db
from settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST
from blueprint_eprotocol import eprotocol as eprotocol_v1

app = Flask(__name__)

app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


db.init_app(app)


# https://medium.com/@karthikeyan.ranasthala/build-a-jwt-based-authentication-rest-api-with-flask-and-mysql-5dc6d3d1cb82
app.register_blueprint(eprotocol_v1, url_prefix="/api/v1.0/")
