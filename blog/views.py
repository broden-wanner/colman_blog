from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.http import Http404

@login_required
def blogHomeView(request):
	posts = Post.objects.all()
	#Adds most recent date for posts that never had it
	for post in posts:
		if post.edited_date == None:
			if post.edited_date:
				post.most_recent_date = post.edited_date
				post.save()
			else:
				post.most_recent_date = post.published_date
				post.save()
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-most_recent_date')
	return render(request, 'index.html', {'posts': posts})

@login_required
def blogDetailView(request, pk):
	post = get_object_or_404(Post, pk=pk)
	try:
		post = Post.objects.get(pk=pk)
	except Post.DoesNotExist:
		raise Http404("No Post matches given query.")
	try:
		older_post = Post.objects.filter(most_recent_date__lt=post.most_recent_date).order_by('-most_recent_date')[0]
	except (Post.DoesNotExist, IndexError, ValueError):
		older_post = None
	try:
		newer_post = Post.objects.filter(most_recent_date__gt=post.most_recent_date).order_by('most_recent_date')[0]
	except (Post.DoesNotExist, IndexError, ValueError):
		newer_post = None
	return render(request, 'detail.html', {'post': post, 'newer_post': newer_post, 'older_post': older_post})

@login_required
def blogCreateView(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.most_recent_date = timezone.now()
			post.save()
			return redirect('detail', pk=post.pk)
	else:
		form = PostForm()
	return render(request, 'create.html', {'form': form})

@login_required
def blogUpdateView(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		if form.is_valid() and post.author == request.user:
			post = form.save(commit=False)
			post.edited_date = timezone.now()
			post.most_recent_date = timezone.now()
			post.save()
			return redirect('detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
	return render(request, 'edit.html', {'form': form, 'post': post})

@login_required
def blogDeleteView(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST" and post.author == request.user:
		post.delete()
		return redirect('index')
	return render(request, 'delete.html', {'post': post})