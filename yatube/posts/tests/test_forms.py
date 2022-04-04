from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем неавторизованного пользователя
        cls.guest_user = Client()
        # создаем авторизованного пользователя
        cls.user = User.objects.create(username='Dmitriy')
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
        # создаем запись в БД
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.post = Post.objects.create(
            text='Text',
            author=cls.user,
            group=cls.group,
        )
        cls.form_data = {
            'text': 'Text_for_new_post',
            'group': cls.group.id,
            'image': cls.uploaded,
        }
        cls.comment_form_data = {
            'text': 'New comment',
        }

    def test_create_new_post(self):
        """Проверяем корректное создание записи с картинкой в БД."""
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.post.author}'}
        ))
        first_object = Post.objects.first()
        post_text = self.form_data.get('text')
        post_group = self.form_data.get('group')
        post_author = self.user
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(first_object.text, post_text)
        self.assertEqual(first_object.group.id, post_group)
        self.assertEqual(first_object.author, post_author)

    def test_correct_edit_post(self):
        """Проверяем корректную работу редактирования поста."""
        new_form_data = {
            'text': 'Changed text',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}),
            data=new_form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.pk}'}
        ))
        first_object = Post.objects.get(id=self.post.pk)
        post_text = new_form_data.get('text')
        post_group = new_form_data.get('group')
        post_author = self.user
        self.assertEqual(first_object.text, post_text)
        self.assertEqual(first_object.group.id, post_group)
        self.assertEqual(first_object.author, post_author)

    def test_guest_client_create_post_redirect(self):
        """Неавторизованный пользователь, не может создать пост."""
        post_count = Post.objects.count()
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'users:login',) + '?next=' + reverse('posts:post_create'))
        first_object = Post.objects.first()
        post_text = self.form_data.get('text')
        self.assertEqual(Post.objects.count(), post_count)
        self.assertNotEqual(first_object.text, post_text)

    def test_add_comment(self):
        """Проверка создания нового комментария."""
        comments_count = Comment.objects.count()
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            data=self.comment_form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )
        new_comment = Comment.objects.first()
        comment_text = self.comment_form_data.get('text')
        comment_author = self.user
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment_text, new_comment.text)
        self.assertEqual(comment_author, new_comment.author)
