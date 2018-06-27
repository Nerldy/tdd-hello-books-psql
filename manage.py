from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db
from app.models import User
import getpass
from app.auth.helper_funcs import format_inputs
import re

admin_user_schema = {
	'username': {
		'type': 'string',
		'required': True,
		'minlength': 2
	},
	'email': {
		'type': 'string',
		'required': True,
		'maxlength': 100
	},
	'password': {
		'type': 'string',
		'required': True
	},
	'confirm_password': {
		'type': 'string',
		'required': True,
	},
	'is_admin': {
		'type': 'boolean',
		'required': True
	}
}

# Initializing the manager
manager = Manager(app)

# Initialize Flask Migrate
migrate = Migrate(app, db)

# Add the flask migrate
manager.add_command('db', MigrateCommand)


@manager.command
def create_admin():
	"""creates admin"""
	username = format_inputs(input('Enter your username: '))
	email = input('Enter your email: ')
	password = getpass.getpass('Enter password')
	confirm_password = getpass.getpass('Enter your password again: ')

	# check length of username
	if len(username) < 2:
		return print('username cannot be empty and less than two characters')

	# confirm passwords match
	if password != confirm_password:
		return print('passwords do not match')

	# confirm length of password is not less than four
	if len(password) < 4:
		return print('password length must be four or more')

	# validate if email matches the standard
	validate_email = re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)
	if validate_email is None:
		return print("email format must have a local part, the “@” symbol, and the domain")

	try:
		admin = User(
			username=username,
			email=email,
			password=password,
			is_admin=True
		)
		admin.save()
		return print(f'Admin {username} successfully created')
	except Exception as e:
		print(e)


# Run the manager
if __name__ == '__main__':
	manager.run()
