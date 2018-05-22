from flask import Blueprint, request, abort, make_response
from flask.views import MethodView
from app.models import User, Book, BlacklistToken
from app.auth.helper_funcs import response, response_auth, token_required, format_inputs
from sqlalchemy import exc
from cerberus import Validator

auth = Blueprint('auth', __name__)

login_schema = {
	'username': {
		'type': 'string',
		'required': True
	},
	'email': {
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
		'minlength': 2,
		'maxlength': 50
	},
	'email': {
		'type': 'string',
		'required': True,
		'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
		'maxlength': 100
	},
	'password': {
		'type': 'string',
		'required': True,
		'minlength': 2,
		'regex': '(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$'

	},
	'is_admin': {
		'type': 'boolean',
		'required': False
	}
}

validate_user_schema = Validator(user_schema)
validate_login_schema = Validator(login_schema)


class RegisterUser(MethodView):
	"""register user view function"""

	def post(self):
		"""register user, add them to the database"""

		if request.content_type == 'application/json':
			post_data = request.get_json()

			if validate_user_schema.validate(post_data):
				username = post_data.get('username')
				email = post_data.get('email')
				password = post_data.get('password')

				user = User.get_by_email(email)

				if not user:
					new_user = User(
						username=username,
						password=password,
						email=email
					)

					if 'is_admin' in post_data:
						new_user.is_admin = post_data['is_admin']

					token = new_user.save()

					return response_auth('success', 'successfully registered', token, 201)
				else:
					return response('error', 'user already exists, please sign in', 400)

			return response('error', validate_user_schema.errors, 400)
		return response('error', 'content-type must be json format', 400)


# register classes as views
registration_view = RegisterUser.as_view('register')

# end point rules
auth.add_url_rule('/register', view_func=registration_view, methods=['POST'])
