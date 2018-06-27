from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db
from app.models import User

# Initializing the manager
manager = Manager(app)

# Initialize Flask Migrate
migrate = Migrate(app, db)

# Add the flask migrate
manager.add_command('db', MigrateCommand)

@manager.command
def create_superuser():
	"""creates admin"""
	username = input('Enter your username: ')
	email = input('Enter your email: ')
	password = input('Enter your password: ')
	confirm_password = input('Enter your password again: ')

	admin_user = {
		'username': username,

	}

	try:
		admin = User(
			username=username,
			email = email
		)


# Run the manager
if __name__ == '__main__':
	manager.run()
