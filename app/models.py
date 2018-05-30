from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app


class Book(db.Model):
	"""instances a book"""
	__tablename__ = 'books'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	isbn = db.Column(db.String(10), nullable=False, unique=True)
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(
		db.DateTime, default=db.func.current_timestamp(),
		onupdate=db.func.current_timestamp())
	is_borrowed = db.Column(db.Boolean, default=False)
	borrowed_books = db.relationship('BorrowedBook', backref='books', lazy='dynamic')

	def __init__(self, title, isbn):
		self.title = title
		self.isbn = isbn

	def save(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_all():
		return Book.query.all()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def serialize(self):
		"""return a json serialized obj"""
		return {
			"id": self.id,
			'title': self.title,
			'isbn': self.isbn,
			"date_created": self.date_created,
			"date_modified": self.date_modified
		}

	def __repr__(self):
		return f"<Book {self.title}"


class BorrowedBook(db.Model):
	__tablename__ = 'borrowed_books'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
	borrow_date = db.Column(db.DateTime, default=db.func.current_timestamp())
	return_date = db.Column(db.DateTime)


class User(db.Model):
	"""defines users"""
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), index=True, unique=True, nullable=False)
	email = db.Column(db.String(100), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String, nullable=False)
	is_admin = db.Column(db.Boolean, default=False)
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(
		db.DateTime, default=db.func.current_timestamp(),
		onupdate=db.func.current_timestamp())
	borrowed_books = db.relationship('BorrowedBook', backref='users', lazy='dynamic')

	@property
	def password(self):
		"""
		Prevent password from being accessed
		"""
		raise AttributeError('password is not a readable attribute.')

	@password.setter
	def password(self, password):
		"""
		Set password to a hashed password
		"""
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		"""
		Check if hashed password matches actual password
		"""
		return check_password_hash(self.password_hash, password)

	def save(self):
		"""
		save user to database
		"""
		db.session.add(self)
		db.session.commit()
		return self.generate_token(self.id)

	def __repr__(self):
		return f'<user: {self.username}>'

	def generate_token(self, user_id):
		""" Generates the access token"""

		try:
			# set up a payload with an expiration time
			payload = {
				'exp': datetime.utcnow() + timedelta(
					days=app.config.get('AUTH_TOKEN_EXPIRY_DAYS'),
					seconds=app.config.get('AUTH_TOKEN_EXPIRY_SECONDS')
				),
				'iat': datetime.utcnow(),
				'sub': user_id
			}
			# create the byte string token using the payload and the SECRET key
			jwt_string = jwt.encode(
				payload=payload,
				key=str(app.config['SECRET_KEY']),
				algorithm='HS256'
			)

			return jwt_string

		except Exception as e:
			# return an error in string format if an exception occurs
			return str(e)

	@staticmethod
	def decode_token(token):
		"""Decodes the access token from the Authorization header."""
		try:
			# try to decode the token using our SECRET variable
			payload = jwt.decode(token, str(app.config['SECRET_KEY']), algorithms='HS256')
			is_token_blacklisted = BlacklistToken.check_blacklist(token)
			if is_token_blacklisted:
				return 'Token was Blacklisted, Please login In'
			return payload['sub']
		except jwt.ExpiredSignatureError:
			# the token is expired, return an error string
			return "Expired token. Please login to get a new token"
		except jwt.InvalidTokenError:
			# the token is invalid, return an error string
			return "Invalid token. Please register or login"

	@staticmethod
	def get_by_id(user_id):
		"""filter user by id"""
		return User.query.filter(User.id == user_id).first()

	@staticmethod
	def get_by_email(email):
		"""filter user by email"""
		return User.query.filter(User.email == email).first()

	def serialize(self):
		"""returns a json object of the user"""
		return {
			'id': self.id,
			'username': self.username,
			'email': self.email,
			'date_created': self.date_created,
			'date_modified': self.date_modified
		}


class BlacklistToken(db.Model):
	"""table stores invalid tokens"""

	__tablename__ = 'black_list_tokens'
	id = db.Column(db.Integer, primary_key=True)
	token = db.Column(db.String, unique=True, nullable=False)
	blacklisted_on = db.Column(db.DateTime, nullable=False, default=datetime.now())

	def blacklist(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def check_blacklist(token):
		res = BlacklistToken.query.filter_by(token=token).first()

		if res:
			return True
		return False
