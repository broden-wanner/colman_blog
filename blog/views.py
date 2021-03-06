from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Post, Comment, Score
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from collections import OrderedDict

def make_leaderboard():
	#Creates new score for user if they don't have one
	for user in User.objects.all():
		try:
			user_score_clone = Score.objects.get(user=user)
		except (Score.DoesNotExist):
			new_user_score = Score(user=user)
			new_user_score.save()
	#Updates all scores
	scores = Score.objects.all()
	for score in scores:
		score.update_score()
	#Filters scores of only active users
	scores = Score.objects.filter(user__is_active=True).order_by('-score')
	return scores

@login_required
def blogHomeView(request):
	posts = Post.objects.filter(published_date__lte=timezone.now(), author__is_active=True, show=True).order_by('-most_recent_date')
	for post in posts:
		post.update_comments()
	return render(request, 'index.html', {'posts': posts, 'leaderboard': make_leaderboard()})

@login_required
def blogUserView(request):
	written_posts = Post.objects.filter(author=request.user).order_by('-most_recent_date')
	booped_posts = Post.objects.filter(boops=request.user).order_by('-most_recent_date')
	total_boops = 0
	for post in written_posts:
		total_boops += post.boops.count()
	return render(request, 'user_view.html', {
		'written_posts': written_posts,
		'booped_posts': booped_posts,
		'total_boops': total_boops,
		'leaderboard': make_leaderboard(),
	})

@login_required
def blogDetailView(request, slug):
	#Post Section
	post = get_object_or_404(Post, slug=slug)
	#boop and unboop buttons
	if request.user in post.boops.all():
		booped_by_user = True
	else:
		booped_by_user = False
	if request.user in post.unboops.all():
		unbooped_by_user = True
	else:
		unbooped_by_user = False
	#Creates newer and older post buttons
	try:
		older_post = Post.objects.filter(most_recent_date__lt=post.most_recent_date).order_by('-most_recent_date')[0]
	except (Post.DoesNotExist, IndexError, ValueError):
		older_post = None
	try:
		newer_post = Post.objects.filter(most_recent_date__gt=post.most_recent_date).order_by('most_recent_date')[0]
	except (Post.DoesNotExist, IndexError, ValueError):
		newer_post = None
	#Comment Section
	try:
		comment_list = Comment.objects.filter(post__pk=post.pk).order_by('-most_recent_date')
	except (Comment.DoesNotExist, IndexError, ValueError):
		comment_list = None
	#Create Comment Form
	if request.method == "POST":
		create_comment_form = CommentForm(request.POST, prefix="create")
		if create_comment_form.is_valid():
			comment = create_comment_form.save(commit=False)
			comment.post = post
			comment.author = request.user
			comment.published_date = timezone.now()
			comment.most_recent_date = timezone.now()
			comment.save()
			post.update_comments()
			return redirect('detail', slug=post.slug)
	else:
		create_comment_form = CommentForm(prefix="create")
	return render(request, 'detail.html', {
		'post': post,
		'newer_post': newer_post,
		'older_post': older_post,
		'comment_list': comment_list,
		'create_comment_form': create_comment_form,
		'booped_by_user': booped_by_user,
		'unbooped_by_user': unbooped_by_user,
	})

@login_required
def blogCreateView(request):
	if request.method == "POST":
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.most_recent_date = timezone.now()
			post.create_embed_link()
			post.save()
			return redirect('detail', slug=post.slug)
	else:
		form = PostForm()
	return render(request, 'create.html', {'form': form})

@login_required
def blogUpdateView(request, slug):
	post = get_object_or_404(Post, slug=slug)
	if request.method == "POST":
		form = PostForm(request.POST, request.FILES, instance=post)
		if form.is_valid() and post.author == request.user:
			post = form.save(commit=False)
			post.edited_date = timezone.now()
			post.most_recent_date = timezone.now()
			post.create_embed_link()
			post.save()
			return redirect('detail', slug=post.slug)
	else:
		form = PostForm(instance=post)
	return render(request, 'edit.html', {'form': form, 'post': post})

@login_required
def blogDeleteView(request, slug):
	post = get_object_or_404(Post, slug=slug)
	if request.method == "POST" and post.author == request.user:
		post.delete()
		return redirect('index')
	return render(request, 'delete.html', {'post': post})

@login_required
def blogEditComment(request, slug, pk):
	comment = get_object_or_404(Comment, pk=pk)
	if request.method == "POST":
		form = CommentForm(request.POST, instance=comment)
		if form.is_valid() and comment.author == request.user:
			comment = form.save(commit=False)
			comment.edited_date = timezone.now()
			comment.most_recent_date = timezone.now()
			comment.edited = True
			comment.save()
			return redirect('detail', slug=comment.post.slug)
	else:
		form = CommentForm(instance=comment)
	return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

@login_required
def blogToggleBoopUnboop(request, slug, opinion):
	post = get_object_or_404(Post, slug=slug)
	if opinion == 'boop':
		#Handle boop without previous boop or unboop and adds it
		if request.user not in post.boops.all() and request.user not in post.unboops.all():
			post.boops.add(request.user)
		#Handle boop with previous boop and removes it
		elif request.user in post.boops.all() and request.user not in post.unboops.all():
			post.boops.remove(request.user)
		#Handle boop without previous boop but with previous unboop
		elif request.user not in post.boops.all() and request.user in post.unboops.all():
			post.boops.add(request.user)
			post.unboops.remove(request.user)
	if opinion == 'unboop':
		#Handle unboop without previous unboop or boop and adds it
		if request.user not in post.boops.all() and request.user not in post.unboops.all():
			post.unboops.add(request.user)
		#Handle boop with previous boop and removes it
		elif request.user not in post.boops.all() and request.user in post.unboops.all():
			post.unboops.remove(request.user)
		#Handle boop without previous boop but with previous unboop
		elif request.user in post.boops.all() and request.user not in post.unboops.all():
			post.unboops.add(request.user)
			post.boops.remove(request.user)
	return redirect('detail', slug=post.slug)

@login_required
def flappyHawk(request):
	return render(request, 'flappy_hawk.html')