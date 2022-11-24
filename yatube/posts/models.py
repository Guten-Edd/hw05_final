from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title of the group")
    slug = models.SlugField(unique=True, verbose_name="Slug of the group")
    description = models.TextField(verbose_name="Description of the group")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Text of the post")
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Publication data of the post",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Author of the post",
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="The group the post belongs to",
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="The post the comment belongs to",
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name="The author of the comment",
    )
    text = models.TextField(verbose_name="Text of the comment")
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Publication data of the comment",
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name="The user who follow",
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name="The author who is followed",
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            ),
        ]
