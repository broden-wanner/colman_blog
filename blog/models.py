from django.db import models
from django.utils import timezone
import datetime

class Post(models.Model):
	author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	text = models.TextField()
	date_created = models.DateTimeField(default=timezone.now)
	published_date = models.DateTimeField(blank=True)
	edited_date = models.DateTimeField(blank=True, null=True)

	def was_published_or_edited_recently(self):
		now = timezone.now()
		pub_recently = (now - datetime.timedelta(days=1) <= self.published_date <= now)
		if self.edited_date:
			edit_recently = (now - datetime.timedelta(days=1) <= self.edited_date <= now)
		return pub_recently or edit_recently

	def most_recent_date(self):
		if self.edited_date:
			return self.edited_date
		return self.published_date

	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def __str__(self):
		return self.title