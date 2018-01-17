from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	path('', views.blogHomeView, name='index'),
	path('post/<int:pk>/', views.blogDetailView, name='detail'),
	path('post/new/', views.blogCreateView, name='create'),
	path('post/<int:pk>/edit', views.blogUpdateView, name='edit'),
	path('post/<int:pk>/delete', views.blogDeleteView, name='delete'),
	path('post/<int:pk>/comment/edit', views.blogEditComment, name='edit_comment'),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)