from tests.base import BaseTestCase
from app.models import User
from app import db
import unittest
import datetime
import json


class TestAuthBlueprint(BaseTestCase):

	def test_register_user(self):
		"""test api can register user"""
		with self.client:
			res = self.register_user('admin2', 'admin2@mail.com', "12345678Nine#", is_admin=True)
			data = json.loads(res.data.decode())
			self.assertTrue(data['status'] == 'success')
			self.assertTrue(data['message'], 'successfully registered')
			self.assertEqual(res.status_code, 201)
			self.assertTrue(data['auth_token'])

	def test_user_already_exists(self):
		"""test api can't duplicate users"""
		with self.client:
			res = self.register_user('admin2', 'admin2@mail.com', "12345678Nine#", is_admin=True)
			data = json.loads(res.data.decode())
			self.assertEqual(res.status_code, 201)

			res = self.register_user('admin2', 'admin2@mail.com', "12345678Nine#", is_admin=True)
			data = json.loads(res.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertIn('user already exists', str(data))

	def test_content_type_is_json(self):
		"""test api returns error if not json object"""
		with self.client:
			res = self.register_wrong_content_type("bola", 'bola@me.com', "562##,545dfgDWD")
			data = json.loads(res.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertIn('content-type must be json format', data['message'])
			self.assertTrue(res.status_code, 400)

	def test_authentication_error(self):
		"""test json object has all the values needed"""
		with self.client:
			res = res = self.register_does_not_have_needed_properties('mike', 'mike@mail.com')
			data = json.loads(res.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertIn('required field', str(data['message']))

	def test_user_login(self):
		"""test api can login user"""
		with self.client:
			self.register_and_login_in_user()

	def test_user_does_not_exist(self):
		"""test api user doesn't exist"""
		with self.client:
			res = self.client.post(
				'/api/v2/auth/login',
				data=json.dumps(
					dict(
						username='lilbaby',
						email='lilb@mail.com',
						password='harderTHAN.Ev37'
					)
				),
				content_type='application/json'
			)

			data = json.loads(res.data.decode())
			self.assertEqual(res.status_code, 401)
			self.assertIn("user doesn't exist", str(data))

	def test_login_validation_error(self):
		"""test api throws an error if login json validation is not correct"""
		with self.client:
			res = self.client.post(
				'/api/v2/auth/login',
				data=json.dumps(
					dict(
						username='lilbaby',
						password='harderTHAN.Ev37'
					)
				),
				content_type='application/json'
			)

			data = json.loads(res.data.decode())
			self.assertEqual(res.status_code, 401)
			self.assertIn('required field', str(data))

	def test_json_not_detected(self):
		"""test api has no json"""
		with self.client:
			res = self.client.post(
				'/api/v2/auth/login',
				data=json.dumps(
					dict(
						username='lilbaby',
						password='harderTHAN.Ev37',
						email='f@mail.com'
					)
				),
				content_type='text'
			)

			self.assertEqual(res.status_code, 202)
			self.assertIn('content-type must be json', str(res.data))

	def test_user_can_logout(self):
		"""test api can logout user"""
		with self.client:
			# register and login user
			login_res = self.register_and_login_in_user()

			# logout user
			logout_res = self.logout_user(login_res['auth_token'])
			logout_data = json.loads(logout_res.data.decode())
			self.assertEqual(logout_res.status_code, 200)
			self.assertIn('successfully logged out', str(logout_data))

	def test_invalid_token(self):
		"""test api return invalid token error"""
		with self.client:
			res = self.client.post(
				'/api/v2/auth/logout',
				headers=dict(
					Authorization='JOASSsasas4xcdrrldd978Abm'
				)
			)

			data = json.loads(res.data.decode())
			self.assertEqual(res.status_code, 403)
			self.assertTrue(data['message'] == 'provide a valid token')

	def test_no_authorization_header(self):
		"""test api has no authorization header"""
		with self.client:
			response = self.client.post(
				'/api/v2/auth/logout',
			)
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertIn('provide an Authorization header', str(data))
			self.assertEqual(response.status_code, 403)

	def test_user_token_was_blacklisted(self):
		"""test api blacklists token"""
		with self.client:
			# Register and login user
			login_data = self.register_and_login_in_user()
			# Logout user
			logout_response = self.logout_user(login_data['auth_token'])
			logout_data = json.loads(logout_response.data.decode())
			self.assertEqual(logout_response.status_code, 200)
			self.assertTrue(logout_data['status'] == 'success')
			self.assertTrue(logout_data['message'] == 'successfully logged out')

			logout_again_response = self.logout_user(login_data['auth_token'])
			logout_again_data = json.loads(logout_again_response.data.decode())
			self.assertEqual(logout_again_response.status_code, 401)
			self.assertTrue(logout_again_data['status'] == 'error')
			self.assertTrue(logout_again_data['message'] == 'Token was Blacklisted, Please login In')

	# use functions
	def register_wrong_content_type(self, username, email, password):
		"""this function uses content-type: text"""
		return self.client.post(
			'/api/v2/auth/register',
			content_type='text',
			data=json.dumps(dict(username=username, email=email, password=password)))

	def register_does_not_have_needed_properties(self, username, email):
		"""this function does not include password property"""
		return self.client.post(
			'/api/v2/auth/register',
			content_type='application/json',
			data=json.dumps(dict(username=username, email=email)))

	def register_and_login_in_user(self):
		"""
		Helper method to sign up and login a user
		:return: Json login response
		"""
		reg_user = self.register_user('lilbaby', 'lilb@mail.com', 'harderTHAN.Ev37', False)
		data = json.loads(reg_user.data.decode())
		self.assertEqual(reg_user.status_code, 201)
		self.assertIn('successfully registered', str(data))

		# login user
		login_res = self.client.post(
			'/api/v2/auth/login',
			data=json.dumps(
				dict(
					username='lilbaby',
					email='lilb@mail.com',
					password='harderTHAN.Ev37'
				)
			),
			content_type='application/json'
		)
		login_data = json.loads(login_res.data.decode())
		self.assertIn('successfully logged in', str(login_data))
		return login_data

	def logout_user(self, token):
		logout_res = self.client.post(
			'/api/v2/auth/logout',
			headers=dict(
				Authorization=f'Bearer {token}'
			)
		)
		return logout_res
