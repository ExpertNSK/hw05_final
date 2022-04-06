from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post

User = get_user_model()


class FollowPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Dmitriy')
        cls.follower = Client()
        cls.follower.force_login(cls.user)

        cls.user2 = User.objects.create(username='Wioletta')
        cls.not_follower = Client()
        cls.not_follower.force_login(cls.user2)

        cls.user3 = User.objects.create(username='Author')
        cls.author = Client()
        cls.author.force_login(cls.user3)

    def _create_follow_obj_and_new_post(self):
        Follow.objects.create(user=self.user, author=self.user3)
        new_post = Post.objects.create(
            text='Text',
            author=self.user3,
        )
        return new_post

    def test_follow_page_show_new_post(self):
        """Новый пост появляется в ленте тех, кто подписан на автора."""
        new_post = self._create_follow_obj_and_new_post()
        response = self.follower.get(reverse('posts:follow'))
        self.assertIn(new_post, response.context['page_obj'])

    def test_not_follower(self):
        """Новый пост не появляется в ленте тех, кто не подписан на автора."""
        new_post = self._create_follow_obj_and_new_post()
        response = self.not_follower.get(
            reverse('posts:follow')
        )
        self.assertIsNot(
            new_post,
            response.context['page_obj']
        )
