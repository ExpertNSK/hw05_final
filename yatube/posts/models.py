from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"post_id": self.pk})


class Comment(CreatedModel):
    post = models.ForeignKey(
        to=Post,
        verbose_name='Пост',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        to=User,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите комменатрий'
    )


class Follow(CreatedModel):
    user = models.ForeignKey(
        to=User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        to=User,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='user_and_author_uniq_together'),
        ]
