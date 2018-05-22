from tests.base import BaseTestCase
import json


class TestErrorPages(BaseTestCase):
	def test_404_error(self):
		"""test 404 error"""
		with self.client:
			res = self.client.post(
				'/api/56',
				content_type='application/json'
			)
			self.assertIn('not found', str(res.data))
			self.assertEqual(res.status_code, 404)
