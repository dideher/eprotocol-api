# app.py
import os
import hashlib
from flask import Flask, jsonify, json
from werkzeug.exceptions import HTTPException
from extensions import db, auth
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


# Verify the username and password
@auth.verify_password
def verify_password(username, password):
    expected_hash = os.getenv(f"BASIC_AUTH_{username}", None)
    if expected_hash is None:
        return None
    
    if expected_hash == hashlib.sha256(password.encode()).hexdigest():
        return username

    return None


# Error handler for HTTP errors (like 404, 500)
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Handles HTTP exceptions and returns JSON with a custom message."""
    response = e.get_response()
    response.data = json.dumps({
        "success": False,
        "code": e.code,
        "error": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

# Generic exception handler (non-HTTP exceptions)
@app.errorhandler(Exception)
def handle_generic_exception(e):
    """Handles all uncaught exceptions and returns a generic error response."""
    app.logger.error(f"Unexpected error: {e}")
    response = jsonify({
        "success": False,
        "code": 500,
        "error": "Internal Server Error",
        "description": "An unexpected error occurred. Please try again later."
    })
    return response, 500


# https://medium.com/@karthikeyan.ranasthala/build-a-jwt-based-authentication-rest-api-with-flask-and-mysql-5dc6d3d1cb82
app.register_blueprint(eprotocol_v1, url_prefix="/api/v1.0/")
