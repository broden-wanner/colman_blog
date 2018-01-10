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
	most_recent_date = models.DateTimeField(blank=True, null=True)
	comments = models.IntegerField(default=0)

	def was_published_or_edited_recently(self):
		now = timezone.now()
		pub_recently = (now - datetime.timedelta(days=1) <= self.published_date <= now)
		if self.edited_date:
			edit_recently = (now - datetime.timedelta(days=1) <= self.edited_date <= now)
		else:
			edit_recently = False
		return pub_recently or edit_recently

	def update_comments(self):
		self.comments = int(Comment.objects.filter(post__pk=self.pk).count())

	def __str__(self):
		return self.title

class Comment(models.Model):
	post = models.ForeignKey('Post', on_delete=models.CASCADE)
	author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	text = models.TextField()
	date_created = models.DateTimeField(default=timezone.now)
	published_date = models.DateTimeField(blank=True)
	edited_date = models.DateTimeField(blank=True, null=True)
	most_recent_date = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return "Comment on post %s" % (self.post.title)

	def time_since_post(self):
		now = timezone.now()
		time_since = now - self.most_recent_date
		if time_since < datetime.timedelta(minutes=1):
			return "%i seconds ago" % (time_since.seconds)
		elif time_since < datetime.timedelta(hours=1):
			return "%i minutes ago" % (time_since.seconds / 60)
		elif time_since < datetime.timedelta(days=1):
			return "%i hours ago" % (time_since.seconds / 60 / 60)
		elif time_since < datetime.timedelta(weeks=1):
			return "%i days ago" % (time_since.days)
		elif time_since < datetime.timedelta(weeks=4):
			return "%i weeks ago" % (time_since.days / 7)
		elif time_since < datetime.timedelta(weeks=52):
			return "%i months ago" % (time_since.days / 30)
		else:
			return "%i years ago" % (time_since / 365)
			