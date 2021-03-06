from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from app.models import User, BlacklistToken
from app.auth.helper_funcs import response, response_auth, token_required, format_inputs
from cerberus import Validator
import re

auth = Blueprint('auth', __name__)

login_schema = {
	'username': {
		'type': 'string',
		'required': True
	},
	'password': {
		'type': 'string',
		'required': True,
	}
}

user_schema = {
	'username': {
		'type': 'string',
		'required': True,
		'minlength': 1,
		'maxlength': 50
	},
	'email': {
		'type': 'string',
		'required': True,
		'maxlength': 100
	},
	'password': {
		'type': 'string',
		'required': True,
		'minlength': 8
	},
	'confirm_password': {
		'type': 'string',
		'required': True,
	}
}

reset_password_schema = {
	'old_password': {
		'type': 'string',
		'required': True

	},
	'new_password': {

		'type': 'string',
		'required': True,
		'minlength': 8
	}
}

validate_user_schema = Validator(user_schema)
validate_login_schema = Validator(login_schema)
validate_reset_password_schema = Validator(reset_password_schema)


class RegisterUser(MethodView):
	"""register user view function"""

	def post(self):
		"""register user, add them to the database"""

		if request.content_type == 'application/json':

			try:
				post_data = request.get_json()

				if validate_user_schema.validate(post_data):

					if post_data.get('username').isalnum() is False:
						return response('error', 'username can only have numbers and letters', 400)

					username = format_inputs(request.json.get('username'))
					email = post_data.get('email')
					password = post_data.get('password')
					confirm_password = post_data.get('confirm_password')

					# validate if email matches the standard
					validate_email = re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)
					if validate_email is None:
						return response('error', "email format must have a local part, the “@” symbol, and the domain", 400)

					# confirm password match
					if password != confirm_password:
						return response('error', 'password don\'t match', 400)

					user = User.get_by_email(email)

					if not user:
						new_user = User(
							username=username,
							password=password,
							email=email
						)
						# create token
						token = new_user.save()

						return response_auth('success', 'successfully registered', token, 201)
					else:
						return response('error', 'user already exists, please sign in', 400)

				return response('error', validate_user_schema.errors, 400)
			except Exception as e:
				return response('error', 'username already exists', 400)
		return response('error', 'content-type must be json format', 400)


class LoginUser(MethodView):
	"""class to log in user"""

	def post(self):
		if request.content_type == 'application/json':
			post_data = request.get_json()

			if validate_login_schema.validate(post_data):
				username = post_data.get('username')
				password = post_data.get('password')

				user = User.query.filter(User.username == username).first()

				if user and user.verify_password(password):
					return make_response(jsonify({
						'status': 'success',
						'message': 'successfully logged in',
						'auth_token': user.generate_token(user.id).decode("utf-8"),
						"is_admin": user.is_admin
					})), 200
				return response('error', "user doesn't exist or password is incorrect or username and email do not match", 401)

			return response('error', validate_login_schema.errors, 401)
		return response('error', 'content-type must be json', 400)


class LogoutUser(MethodView):
	"""class to log out user"""

	def post(self):
		auth_header = request.headers.get('Authorization')
		if auth_header:
			try:
				auth_token = auth_header.split(" ")[1]
			except IndexError:
				return response('error', 'provide a valid token', 403)
			else:
				decoded_token_response = User.decode_token(auth_token)
				if not isinstance(decoded_token_response, str):
					token = BlacklistToken(token=auth_token)
					token.blacklist()
					return response('success', 'successfully logged out', 200)
				return response('error', decoded_token_response, 401)
		return response('error', 'provide an Authorization header', 403)


@auth.route('/reset-password', methods=['POST'])
@token_required
def reset_password(current_user):
	"""this function resets password"""
	if request.content_type == 'application/json':
		data = request.get_json()

		# validate the json data matches the schema
		if validate_reset_password_schema.validate(data):
			old_password = data.get('old_password')
			new_password = data.get('new_password')

			if old_password == new_password:
				return response('error', 'old password cannot be the same as new password', 406)

			# check if old password match. If they do, update password
			if current_user.verify_password(old_password):
				current_user.password = new_password
				current_user.save()

				# log out user
				auth_header = request.headers.get('Authorization')
				auth_token = auth_header.split(" ")[1]
				token = BlacklistToken(token=auth_token)
				token.blacklist()
				return response('success', 'password reset successful', 200)
			return response('error', "password don't match", 401)

		return response('error', validate_reset_password_schema.errors, 401)
	return response('error', 'Content-type must be json', 400)


# register classes as views
registration_view = RegisterUser.as_view('register')
login_view = LoginUser.as_view('login')
logout_view = LogoutUser.as_view('logout')

# end point rules
auth.add_url_rule('/register', view_func=registration_view, methods=['POST'])
auth.add_url_rule('/login', view_func=login_view, methods=['POST'])
auth.add_url_rule('/logout', view_func=logout_view, methods=['POST'])
