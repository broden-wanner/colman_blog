from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Comment
from django.utils import timezone

def create_author():
	user = User.objects.create_user(username='testuser', password='testpassword')
	return user

def create_random_post():
	return Post.objects.create(author=create_author(), title='Test Post', text='Lorem ipsum dolor amet...', published_date=timezone.now())

class AcessTests(TestCase):
	def test_index_page_status_code_for_nonusers(self):
		response = self.client.get('/')
		self.assertEquals(response.status_code, 302)
	def test_detial_page_status_code_for_nonusers(self):
		test_post = create_random_post()
		response = self.client.get('/post/%i' % (test_post.pk))
		self.assertEquals(response.status_code, 301)
	def test_create_page_status_code_for_nonusers(self):
		response = self.client.get('/post/new')
		self.assertEquals(response.status_code, 301)
	def test_edit_page_status_code_for_nonusers(self):
		test_post = create_random_post()
		response = self.client.get('/post/%i/edit' % (test_post.pk))
		self.assertEquals(response.status_code, 302)

