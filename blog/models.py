from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import datetime

class Post(models.Model):
	author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	text = models.TextField()
	slug = models.SlugField(unique=True, blank=True, null=True)
	published_date = models.DateTimeField(blank=True, default=timezone.now)
	edited_date = models.DateTimeField(blank=True, null=True)
	most_recent_date = models.DateTimeField(blank=True, null=True)
	comment_count = models.IntegerField(default=0)
	boops = models.ManyToManyField('auth.User', related_name='post_boops', blank=True)
	unboops = models.ManyToManyField('auth.User', related_name='post_unboops', blank=True)
	image = models.ImageField(blank=True, null=True, upload_to='images/')
	youtube_video = models.URLField(max_length=300, blank=True, null=True)
	embed_link = models.URLField(max_length=300, blank=True, null=True)
	show = models.BooleanField(default=True)

	def __str__(self):
		return self.title

	def was_published_or_edited_recently(self):
		now = timezone.now()
		pub_recently = (now - datetime.timedelta(days=1) <= self.published_date <= now)
		if self.edited_date:
			edit_recently = (now - datetime.timedelta(days=1) <= self.edited_date <= now)
		else:
			edit_recently = False
		return pub_recently or edit_recently

	def update_comments(self):
		self.comment_count = int(Comment.objects.filter(post__pk=self.pk).count())

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Post, self).save(*args, **kwargs)

	def create_embed_link(self):
		if self.youtube_video:
			end_code = self.youtube_video[self.youtube_video.find('=') + 1:]
			self.embed_link = 'https://www.youtube.com/embed/' + end_code + '?rel=0'

class Score(models.Model):
	user = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
	score = models.IntegerField(default=0)

	def __str__(self):
		return "Score of %i for %s" % (self.score, self.user.username)

	def update_score(self, *additional_scores):
		user_posts = Post.objects.filter(author=self.user)
		user_score = 0
		for post in user_posts:
			#Add 2 for boops
			user_score += post.boops.count() * 2
			#Add 1 for post
			user_score += 1
			#Subtract 1 for unboops
			user_score -= post.unboops.count()
		self.score = user_score
		for score in additional_scores:
			self.score += score
		self.save()

class Comment(models.Model):
	post = models.ForeignKey('Post', on_delete=models.CASCADE)
	author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	text = models.TextField()
	published_date = models.DateTimeField(blank=True, default=timezone.now)
	edited_date = models.DateTimeField(blank=True, null=True)
	most_recent_date = models.DateTimeField(blank=True, null=True)
	edited = models.BooleanField(default=False)

	def __str__(self):
		return "Comment on post %s" % (self.post.title)

	def time_since_post(self):
		now = timezone.now()
		time_since = now - self.most_recent_date
		if time_since < datetime.timedelta(minutes=1):
			return "%i seconds ago" % (time_since.seconds)
		elif time_since < datetime.timedelta(hours=1):
			elapsed_time = time_since.seconds / 60
			if int(elapsed_time) == 1:
				return "1 minute ago"
			else:
				return "%i minutes ago" % (elapsed_time)
		elif time_since < datetime.timedelta(days=1):
			elapsed_time = time_since.seconds / 3600
			if int(elapsed_time) == 1:
				return "1 hour ago"
			else:
				return "%i hours ago" % (elapsed_time)
		elif time_since < datetime.timedelta(weeks=1):
			elapsed_time = time_since.days
			if int(elapsed_time) == 1:
				return "1 day ago"
			else:
				return "%i days ago" % (elapsed_time)
		elif time_since < datetime.timedelta(weeks=4):
			elapsed_time = time_since.days / 7
			if int(elapsed_time) == 1:
				return "1 week ago"
			else:
				return "%i weeks ago" % (elapsed_time)
		elif time_since < datetime.timedelta(weeks=52):
			elapsed_time = time_since.days / 30
			if int(elapsed_time) == 1:
				return "1 month ago"
			else:
				return "%i months ago" % (elapsed_time)
		else:
			elapsed_time = time_since.days / 365
			if int(elapsed_time) == 1:
				return "1 year ago"
			else:
				return "%i years ago" % (elapsed_time)