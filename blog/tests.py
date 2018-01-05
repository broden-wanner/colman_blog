from django.test import TestCase

class SimpleTests(TestCase):
	def test_index_page_status_code(self):
		response = self.client.get('/')
		self.assertEquals(response.status_code, 200)
	def test_index_page_context(self):
		response = self.client.get('/')
		self.assertTrue('posts' in response.context)