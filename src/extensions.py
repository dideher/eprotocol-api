from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth

db = MySQL()
auth = HTTPBasicAuth()