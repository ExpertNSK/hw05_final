from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.guest_user = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост',
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.post.author}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        cls.list_url_for_all_users = {
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.post.author}/',
            f'/posts/{cls.post.pk}/',
        }

    def test_urls_uses_correct_templates(self):
        """Проверка, что URL'ы используют соответствующие шаблоны."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """Проверка, что при запросе несуществующей
           страницы будет возвращён код 404."""
        response = self.guest_user.get('/not_created/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_home_url_exists_at_desired_location(self):
        """Проверка, что список url list for all users,
           доступен любому пользователю"""
        for address in self.list_url_for_all_users:
            with self.subTest(address=address):
                response = self.guest_user.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_create_post_exists_at_desired_location_authorized(self):
        """Проверка, что страница /create/
           доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_create_posts_page_redirect_not_authorized(self):
        """Страница /create/ переадресует на
           login не авторизованного пользователя."""
        response = self.guest_user.get('/create/')
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create')
        )

    def test_url_edit_post_exists_at_desired_location_author(self):
        """Проверка, что <post_id>/edit/ доступен автору поста."""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_edit_post_redirect_not_author(self):
        """Проверка, что post_edit переадресует не автора поста."""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/'
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.pk}'}
        ))

    def test_url_edit_not_author_redirect_to_detail(self):
        """Проверка, что авторизованный пользователь, не автор поста,
           будет перенаправлен на страницу поста."""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.pk}/'
        )
