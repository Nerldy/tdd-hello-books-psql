from tests.base import BaseTestCase
import json

URL_BOOKS = '/api/v2/books'
URL_AUTH = '/api/v2/auth/'


class TestBookMethods(BaseTestCase):
	"""test books methods and views"""

	def test_api_redirects_to_docs(self):
		"""test api / redirects to the documentation"""

		with self.client:
			get_doc = self.client.get('/')
			self.assertTrue(get_doc.status_code == 302)

	def test_user_can_create_a_book(self):
		"""test user can create a book"""

		with self.client:
			add_book = {
				'title': 'Hello Books',
				'isbn': '5698745124'
			}
			login_data = self.login_test_user()
			token = login_data['auth_token']
			res = self.client.post(
				f'{URL_BOOKS}',
				headers=dict(Authorization=f'Bearer {token}'),
				content_type='application/json',
				data=json.dumps(add_book)
			)
			res2 = json.loads(res.data.decode())
			self.assertIn('success', str(res2))

	def test_book_isbn_length_must_be_ten(self):
		"""test book isbn number is not equal to 10"""

		with self.client:
			add_book = {
				'title': 'Hello Books',
				'isbn': '56987451'
			}
			login_data = self.login_test_user()
			token = login_data['auth_token']
			res = self.client.post(
				f'{URL_BOOKS}',
				headers=dict(Authorization=f'Bearer {token}'),
				content_type='application/json',
				data=json.dumps(add_book)
			)
			res2 = json.loads(res.data.decode())
			self.assertIn('isbn length must be 10', str(res2))

	def test_book_isbn_must_only_be_numbers(self):
		"""test book isbn must only be numbers"""

		with self.client:
			add_book = {
				'title': 'Hello Books',
				'isbn': '56987451Ky'
			}
			login_data = self.login_test_user()
			token = login_data['auth_token']
			res = self.client.post(
				f'{URL_BOOKS}',
				headers=dict(Authorization=f'Bearer {token}'),
				content_type='application/json',
				data=json.dumps(add_book)
			)
			res2 = json.loads(res.data.decode())
			self.assertIn('isbn must only include numbers', str(res2))
			self.assertEqual(res.status_code, 400)

	def test_book_validation_error(self):
		"""test book requires field"""

		with self.client:
			add_book = {
				'title': 'Hello Books'
			}
			login_data = self.login_test_user()
			token = login_data['auth_token']
			res = self.client.post(
				f'{URL_BOOKS}',
				headers=dict(Authorization=f'Bearer {token}'),
				content_type='application/json',
				data=json.dumps(add_book)
			)
			res2 = json.loads(res.data.decode())
			self.assertIn('required field', str(res2))
			self.assertEqual(res.status_code, 400)

	def test_book_must_be_json(self):
		"""test json object not detected"""

		with self.client:
			add_book = {
				'title': 'Hello Books',
				'isbn': "8985652145"
			}
			login_data = self.login_test_user()
			token = login_data['auth_token']
			res = self.client.post(
				f'{URL_BOOKS}',
				headers=dict(Authorization=f'Bearer {token}'),
				content_type='text',
				data=json.dumps(add_book)
			)
			res2 = json.loads(res.data.decode())
			self.assertIn('Content-type must be json', str(res2))
			self.assertEqual(res.status_code, 202)

	def test_get_book_with_id(self):
		"""test api can get a book with ID"""
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		# get book id
		book = self.client.get(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json'
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['books']['title'] == 'hello books')

	def test_get_book_id_is_integer(self):
		"""test api book ID is integer"""
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		# get book id
		book = self.client.get(
			f'{URL_BOOKS}/1p',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json'
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['message'] == 'please provide a book id. ID must be integer')
		self.assertEqual(book.status_code, 400)

	def test_get_book_with_id_does_not_exist(self):
		"""test api get book ID does not exist"""
		login_data = self.register_and_login_in_user()
		token = login_data['auth_token']

		# get book id
		book = self.client.get(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json'
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['message'] == 'book not found')
		self.assertEqual(book.status_code, 404)

	def test_api_can_update_book(self):
		"""test API can update book"""

		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		# update book
		book = self.client.put(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(
				dict(
					title='updated book'
				)
			)
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['title'] == 'updated book')

	def test_api_update_book_validation_error(self):
		"""test API returns validation error"""

		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)
		empty_book = {}
		# update book
		book = self.client.put(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(
				empty_book
			)
		)

		book_res = json.loads(book.data.decode())
		self.assertIn('Nothing was changed', str(book_res))

	def test_api_update_book_id_is_integer(self):
		"""test API update book ID is integer"""

		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)
		# update book
		book = self.client.put(
			f'{URL_BOOKS}/1k',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(
				dict(
					title='updated book'
				)
			)
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['message'] == 'please provide a book id. ID must be integer')

	def test_api_update_book_with_id_does_not_exist(self):
		"""test API update book ID does not exist"""

		login_data = self.login_test_user()
		token = login_data['auth_token']

		book = self.client.put(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(
				dict(
					title='updated book'
				)
			)
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['message'] == 'book with id 1 does not exist')
		self.assertTrue(book_res['status'] == 'error')

	def test_api_update_book_is_not_json(self):
		"""test API update book content type is not json"""

		login_data = self.login_test_user()
		token = login_data['auth_token']

		book = self.client.put(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='text',
			data=json.dumps(
				dict(
					title='updated book'
				)
			)
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['message'] == 'Content-type must be json')
		self.assertTrue(book_res['status'] == 'error')
		self.assertTrue(book.status_code, 202)

	def test_api_user_is_not_admin(self):
		"""test API is not admin"""

		# register the user
		reg_user = self.register_user('lilbaby', 'lilb@mail.com', 'test#op3456', 'test#op3456')
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
		token = login_data['auth_token']

		book = self.client.put(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='text',
			data=json.dumps(
				dict(
					title='updated book'
				)
			)
		)

		book_res = json.loads(book.data.decode())
		self.assertTrue(book_res['error'] == 'forbidden')
		self.assertTrue(book.status_code == 403)

	def test_get_all_books(self):
		"""test api can return books from the database"""

		# create book
		book_1 = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}
		book_2 = {
			'title': 'Hello Books 2',
			'isbn': '8765456766'
		}
		login_data = self.login_test_user()
		token = login_data['auth_token']
		post_book_1 = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(book_1)
		)

		post_book_2 = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(book_2)
		)

		res = self.client.get(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'))

		res_data = json.loads(res.data.decode())
		self.assertEqual(len(res_data.get('books')), 2)

	def test_get_all_books_with_pagination(self):
		"""test api can return books from the database with pagination"""

		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}

		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		# get books
		res = self.client.get(
			f'{URL_BOOKS}?limit=1&page=1',
			headers=dict(Authorization=f'Bearer {token}'))

		pagination = json.loads(res.data.decode())
		self.assertTrue(pagination['current_page'] == 1)
		self.assertTrue(pagination['has_next'] == False)
		self.assertTrue(pagination['has_prev'] == False)
		self.assertTrue(pagination['total_pages'] == 1)

	def test_delete_book(self):
		"""test api can delete book with id"""

		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}

		login_data = self.login_test_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		# delete book
		del_book = self.client.delete(
			f'{URL_BOOKS}/1',
			headers=dict(Authorization=f'Bearer {token}')
		)

		res3 = json.loads(del_book.data.decode())
		self.assertTrue(res3['message'] == 'book with id 1 has been deleted')

	# useful functions
	def register_user(self, username, email, password, confirm_password):
		"""
		Helper method for registering a user with dummy data
		:return:
		"""
		return self.client.post(
			f'{URL_AUTH}register',
			content_type='application/json',
			data=json.dumps(dict(username=username, email=email, password=password, confirm_password=confirm_password)))

	def login_and_add_book(self):
		"""
		this will login and create a book
		:return:
		"""
		# create book
		add_book = {
			'title': 'Hello Books',
			'isbn': '5698745124'
		}

		login_data = self.register_and_login_in_user()
		token = login_data['auth_token']
		res = self.client.post(
			f'{URL_BOOKS}',
			headers=dict(Authorization=f'Bearer {token}'),
			content_type='application/json',
			data=json.dumps(add_book)
		)

		return res

	def register_and_login_in_user(self):
		"""
		Helper method to sign up and login a user
		:return: Json login response
		"""
		reg_user = self.register_user('lilbaby', 'lilb@mail.com', 'test#op3456', 'test#op3456')
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
