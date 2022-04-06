from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
        # создаем авторизованного клиента
        cls.guest_user = Client()
        cls.user = User.objects.create_user(username='Dmitriy')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # создаем тестовую картинку
        picture = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=picture,
            content_type='image/gif',
        )
        # создаем записи в БД
        cls.group = Group.objects.create(
            title='Title',
            slug='test_slug',
            description='Description',
        )
        cls.post = Post.objects.create(
            text='Text',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        # проверямые списки
        cls.templates_pages_name = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse(
                'posts:groups',
                kwargs={'slug': 'test_slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{cls.post.author}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{cls.post.pk}'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{cls.post.pk}'}
            ): 'posts/create_post.html'
        }
        cls.forms_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

    def _context_check(self, first_object):
        """Проверка контекста."""
        post_text = first_object.text
        post_author = first_object.author.username
        post_group = first_object.group.title
        post_image = first_object.image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author.username)
        self.assertEqual(post_group, self.post.group.title)
        self.assertEqual(post_image, self.post.image)

    def _paginator_check(self, response):
        """Проверка ожидаемого кол-ва записей."""
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_pages_used_correct_template(self):
        """URL адреса используют правильные шаблоны."""
        for reverse_name, template in self.templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом,
            на странице ожидаемое кол-во записей."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        first_object = response.context['page_obj'][0]
        self._context_check(first_object)
        self._paginator_check(response)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом,
            на странице ожидаемое кол-во записей."""
        response = self.authorized_client.get(
            reverse('posts:groups', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self._context_check(first_object)
        self._paginator_check(response)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            )
        )
        first_object = response.context['page_obj'][0]
        self._context_check(first_object)
        self._paginator_check(response)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.pk}'}
            )
        )
        first_object = response.context['post']
        self._context_check(first_object)

    def test_post_create_show_correct_form(self):
        """Форма создания поста сформирована с правильными полями."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        response_is_edit = response.context.get('is_edit')
        for value, expected in self.forms_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)
                self.assertEqual(response_is_edit, None)

    def test_post_edit_show_correct_form(self):
        """Форма редактирования поста сформирована с правильными полями."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.pk}'}
        ))
        response_is_edit = response.context.get('is_edit')
        for value, expected in self.forms_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)
                self.assertEqual(response_is_edit, True)

    def test_correct_show_new_post(self):
        """Проверка отображения нового поста c группой."""
        new_group = Group.objects.create(
            title='Title_2',
            slug='test_slug_2',
            description='desription'
        )
        new_post = Post.objects.create(
            text='Проверка отображения',
            author=self.user,
            group=new_group,
        )
        response_main_page = self.authorized_client.get(
            reverse('posts:main_page')
        )
        response_group_list = self.authorized_client.get(reverse(
            'posts:groups',
            kwargs={'slug': f'{new_post.group.slug}'}
        ))
        response_profile = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': f'{new_post.author}'}
        ))
        response_another_group = self.authorized_client.get(reverse(
            'posts:groups',
            kwargs={'slug': self.group.slug}
        ))
        self.assertIn(new_post, response_main_page.context['page_obj'])
        self.assertIn(new_post, response_group_list.context['page_obj'])
        self.assertIn(new_post, response_profile.context['page_obj'])
        self.assertIsNot(new_post, response_another_group.context['page_obj'])

    def test_main_page_cache(self):
        """Проверяем, что на главной странице работает кэш."""
        response = self.guest_user.get(reverse('posts:main_page'))
        content_old = response.content
        Post.objects.create(
            text='test cache index page',
            author=self.user,
            group=self.group
        )
        response = self.guest_user.get(reverse('posts:main_page'))
        self.assertEqual(response.content, content_old)
        cache.clear()
        response = self.guest_user.get(reverse('posts:main_page'))
        self.assertNotEqual(response.content, content_old)

    def test_follow(self):
        """Проверяем, что авторизованный пользователь может
        подписаться на других пользователей"""
        follow_start = Follow.objects.count()
        self.authorized_follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.post.author}))
        follow = Follow.objects.first()
        follow_count = Follow.objects.count()
        self.assertEqual(follow_count, follow_start + 1)
        self.assertEqual(follow.user, self.follower)
        self.assertEqual(follow.author, self.user)

    def test_unfollow(self):
        """Проверяем, что авторизованный пользователь может
        отписаться от других пользователей"""
        Follow.objects.create(user=self.follower, author=self.user)
        follow_start = Follow.objects.count()
        self.authorized_follower.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user}))
        follow_counts = Follow.objects.count()
        self.assertEqual(follow_counts, follow_start - 1)
