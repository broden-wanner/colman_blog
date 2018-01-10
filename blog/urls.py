from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('', views.blogHomeView, name='index'),
	path('post/<int:pk>/', views.blogDetailView, name='detail'),
	path('post/new/', views.blogCreateView, name='create'),
	path('post/<int:pk>/edit', views.blogUpdateView, name='edit'),
	path('post/<int:pk>/delete', views.blogDeleteView, name='delete'),
]