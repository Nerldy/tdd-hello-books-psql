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
