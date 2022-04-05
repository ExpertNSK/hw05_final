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


    def test_follow_page_show_relevant_posts(self):
        """Новый пост появляется в ленте тех, кто подписан на автора."""
        Follow.objects.create(user=self.user, author=self.user3)
        new_post = Post.objects.create(
            text='Text',
            author=self.user3,
        )
        response_for_follower = self.follower.get(reverse('posts:follow'))
        response_for_not_follower = self.not_follower.get(reverse('posts:follow'))
        self.assertIn(new_post, response_for_follower.context['page_obj'])
        self.assertIsNot(new_post, response_for_not_follower.context['page_obj'])
