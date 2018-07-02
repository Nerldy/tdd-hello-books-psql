from app import app, db
from flask_testing import TestCase
from app.models import User
import json


class BaseTestCase(TestCase):
	def create_app(self):
		app.config.from_object('app.config.TestingConfig')
		return app

	def setUp(self):
		"""
		Create the database
		:return:
		"""
		db.create_all()
		db.session.commit()
		self.test_user = User(
			username='tester',
			email='tester@mail.com',
			password='tester#Password1',
			is_admin=True
		)
		self.test_user.save()

	def tearDown(self):
		"""
		Drop the database tables and also remove the session
		:return:
		"""
		db.session.remove()
		db.drop_all()

	def register_user(self, username, email, password, confirm_password):
		"""
		Helper method for registering a user with dummy data
		:return:
		"""
		return self.client.post(
			'/api/v2/auth/register',
			content_type='application/json',
			data=json.dumps(dict(username=username, email=email, password=password, confirm_password=confirm_password)))

	def get_user_token(self):
		"""
		Get a user token
		:return:
		"""
		auth_res = self.register_user('admin1', 'admin1@mail.com', 'PO,KL56mnopfg1', True)
		return json.loads(auth_res.data.decode())['auth_token']
