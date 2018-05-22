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
