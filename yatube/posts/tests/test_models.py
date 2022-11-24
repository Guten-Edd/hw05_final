from django.test import TestCase
from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title,
                         'test_models_have_correct_object_names работает '
                         'некорректно у модели Group')
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15],
                         'test_models_have_correct_object_names '
                         'работает некорректно у модели Post')
