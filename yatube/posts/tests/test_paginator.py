from math import ceil
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from yatube.settings import ENTRIES_PER_PAGE

from ..models import Post

User = get_user_model()


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем авторизованного пользователя
        cls.user = User.objects.create(username='Dmitriy')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # создаем 13 записей в БД
        cls.obj = [
            Post(
                text='Test',
                author=cls.user
            )
            for e in range(13)
        ]
        cls.post = Post.objects.bulk_create(cls.obj)
        cls.posts_count = Post.objects.all().count()
        cls.pages_count = ceil(cls.posts_count / ENTRIES_PER_PAGE)
        cls.posts_last_page = (cls.posts_count - (cls.pages_count - 1)
                               * ENTRIES_PER_PAGE)

    def test_first_page_contains_ten_enries(self):
        """Проверяем, что на первой странице содержатся 10 записей."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        self.assertEqual(len(response.context['page_obj']), ENTRIES_PER_PAGE)

    def test_last_page_contains_correct_numbers_of_enries(self):
        """Проверяем, что на последней странице содержатся ожидаемое
           кол-во записей."""
        response = self.authorized_client.get(
            reverse('posts:main_page') + f'?page={self.pages_count}')
        self.assertEqual(len(
            response.context['page_obj']),
            self.posts_last_page
        )
