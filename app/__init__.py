import os
from flask import Flask, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.url_map.strict_slashes = False


# error handlers
@app.errorhandler(403)
def forbidden(e):
	return jsonify({'error': 'forbidden'}), 403


@app.errorhandler(404)
def page_not_found(e):
	return jsonify({'error': 'not found'}), 404


@app.errorhandler(400)
def bad_request(e):
	return jsonify({"error": 'bad request'}), 400


@app.errorhandler(500)
def internal_server_error(e):
	return jsonify({'error': 'internal server error'}), 500


# app configuration
app_settings = os.getenv(
	'APP_SETTINGS',
	'app.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

# Initialize Flask Sql Alchemy
db = SQLAlchemy(app)

# Import the application views
from app import views

# Register blue prints
from app.auth.views import auth

app.register_blueprint(auth, url_prefix='/api/v2/auth')

from app.books.views import books

app.register_blueprint(books, url_prefix='/api/v2/books')

from app.users.views import users

app.register_blueprint(users, url_prefix='/api/v2/users/books')


# @app.route("/")
# def api_home_page():
# 	return redirect("https://tddhellobookspsql.docs.apiary.io/#")
