from django.urls import path

from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.index, name='main_page'),
    path('group/<slug>/', views.group_posts, name='groups'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<post_id>/comment/', views.add_comment, name='add_comment'),
    path(
        'posts/<post_id>/<comment_id>/delete/',
        views.delete_comment,
        name='delete_comment'
    ),
    path('posts/<post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('follow/', views.follow_index, name='follow'),
    path(
        'profile/<str:username>/follow/',
        views.profile_to_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
