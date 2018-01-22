from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	path('', views.blogHomeView, name='index'),
	path('post/quality-post/new/', views.blogCreateView, name='create'),
	path('post/<slug:slug>/', views.blogDetailView, name='detail'),
	path('post/<slug:slug>/edit', views.blogUpdateView, name='edit'),
	path('post/<slug:slug>/delete', views.blogDeleteView, name='delete'),
	path('post/<slug:slug>/comment/<int:pk>/edit', views.blogEditComment, name='edit_comment'),
	path('post/<slug:slug>/<str:opinion>', views.blogToggleBoopUnboop, name='boop_unboop_toggle'),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)