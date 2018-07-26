from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db
from app.models import User, BorrowedBook, Book
import getpass
from app.auth.helper_funcs import format_inputs
import re
from faker import Faker

fake = Faker()

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


@manager.command
def super_duper_user():
	"""promotes user to admin or downgrades admin to user """

	user_email = input('Enter username email you want to switch: ')
	find_user = User.get_by_email(user_email)

	if find_user:
		change_user = input('press 1 to upgrade user to admin or press 2 to demote admin to user: ')
		if int(change_user) == 1:
			find_user.is_admin = True
			db.session.commit()
			return print('user upgraded')
		if int(change_user) == 2:
			find_user.is_admin = False
			db.session.commit()
			return print('user downgraded')
		return print('You did not press 1 or 2')


@manager.command
def return_user_book():
	"""admin can return user book"""
	user_email = input('Enter user\'s email: ')
	book_id = int(input('Enter book id: '))

	try:

		find_user = User.get_by_email(user_email)
		book_return = BorrowedBook.query.filter(
			db.and_(
				BorrowedBook.book_id == book_id,
				BorrowedBook.user_id == find_user.id,
				BorrowedBook.return_date == None
			)).first()

		if book_return is None:
			return print('book not found')
		else:
			book_borrowed = Book.query.filter_by(id=book_id).first()
			if book_borrowed.is_borrowed:
				book_borrowed.is_borrowed = False
				book_return.return_date = db.func.current_timestamp()
				db.session.commit()
				return print('Book has been returned')

	except Exception as e:
		print(f"error: {e}")


@manager.command
def dummy():
	"""creates 100 fake books and saves them in the database"""
	for i in range(100):
		book = Book(
			title=fake.name(),
			isbn=fake.isbn10(separator='')
		)
		book.save()


# Run the manager
if __name__ == '__main__':
	manager.run()
