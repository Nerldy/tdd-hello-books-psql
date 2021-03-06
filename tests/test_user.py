from tests.base import BaseTestCase
import json

URL_USERS = '/api/v2/users/'
URL_AUTH = '/api/v2/auth/'


class TestUserCases(BaseTestCase):
	"""test user views"""

	def test_books_not_returned(self):
		"""test api can return books not returned"""

		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			'/api/v2/books',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		# borrow book
		res3 = self.client.post(
			f'{URL_USERS}books/1',
			headers=dict(Authorization=f'Bearer {token}')
		)

		# get book not returned
		res4 = self.client.get(
			f'{URL_USERS}books?limit=2&page=1&returned=false',
			headers=dict(Authorization=f'Bearer {token}')
		)
		book_not_returned = json.loads(res4.data.decode())
		self.assertIn('hello books', str(book_not_returned))

	# useful functions
	def login_test_user(self):
		# login user
		login_res = self.client.post(
			f'{URL_AUTH}login',
			data=json.dumps(
				dict(
					username='tester',
					password='tester#Password1'
				)
			),
			content_type='application/json'
		)
		login_data = json.loads(login_res.data.decode())
		self.assertIn('successfully logged in', str(login_data))
		return login_data

	def register_and_login_in_user(self):
		"""
		Helper method to sign up and login a user
		:return: Json login response
		"""
		reg_user = self.register_user('lilbaby', 'lilb@mail.com', 'test#op3456', 'test#op3456', True)
		data = json.loads(reg_user.data.decode())
		self.assertEqual(reg_user.status_code, 201)
		self.assertIn('successfully registered', str(data))

		# login user
		login_res = self.client.post(
			f'{URL_AUTH}login',
			data=json.dumps(
				dict(
					username='lilbaby',
					password='test#op3456'
				)
			),
			content_type='application/json'
		)
		login_data = json.loads(login_res.data.decode())
		self.assertIn('successfully logged in', str(login_data))
		return login_data
