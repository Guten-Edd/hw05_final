from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import tempfile
import shutil
from django.conf import settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    """Проверяем корректость создания нового поста и редиректа
       на страницу профиля
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='new_slug',
            description='описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст4',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'TestUser'}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст4',
                image='posts/small.gif'
            ).exists()
        )

    def test_not_create_post(self):
        """Валидная форма созданная не авторизованным юзером
        НЕ создает запись в Post.
        """
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост сделаный неавторизованным пользователем',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        redirect = reverse("login") + "?next=" + reverse("posts:post_create")
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text='Пост сделаный неавторизованным пользователем',
            ).exists()
        )


class PostEditFormTests(TestCase):
    """Проверяем корректость Редактирования существующего поста
        и редиректа на страницу поста
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user2 = User.objects.create_user(username='TestUserNotAuthor')

        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='new_slug',
            description='описание',
        )
        cls.group2 = Group.objects.create(
            title='Измененная группа',
            slug='edited_slug',
            description='описание Измененнjq группs',
        )
        Post.objects.create(
            author=cls.user,
            text='Текст до изменения',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client_not_athor = Client()

        self.authorized_client.force_login(self.user)
        self.authorized_client_not_athor.force_login(self.user2)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post.
        и проверяется изменение группы
        """
        form_data = {
            'text': 'Тестовый текст после изменения',
            'group': self.group2.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        self.assertEqual(response.context['post'].text, form_data['text'])
        self.assertEqual(response.context['post'].group.title,
                         'Измененная группа')

    def test_edit_post_guest_client(self):
        """Валидная форма с неавторизованным Юзером
        Не редактирует запись в Post.
        """

        form_data = {
            'text': 'Тестовый текст после изменения неавторизованным Юзером',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )

        redirect = (reverse("login") + "?next=" + reverse('posts:post_edit',
                    kwargs={'post_id': '1'}))
        self.assertRedirects(response, redirect)
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст после изменения неавторизованным Юзером',
            ).exists()
        )

    def test_edit_post_Not_author_client(self):
        """Валидная форма с не автором
           Не редактирует запись в Post.
        """

        form_data = {
            'text': 'Тестовый текст после изменения Не Автором поста',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client_not_athor.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )

        redirect = reverse('posts:post_detail', kwargs={'post_id': '1'})
        self.assertRedirects(response, redirect)
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст после изменения Не Автором поста',
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    """Проверяем корректость создания нового Комментария и редиректа
       на страницу профиля
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='new_slug',
            description='описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Текст до изменения',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_post(self):
        """Валидная форма создает запись в Comment."""
        # Подсчитаем количество записей в comment
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Тестовый коммент1',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:add_comment', args='1'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', args='1')
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент1',
            ).exists()
        )

    def test_not_comment_post(self):
        """Валидная форма созданная не авторизованным юзером
        НЕ создает запись в Comment.
        """

        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент1',
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:add_comment', args='1'),
            data=form_data,
            follow=True
        )

        redirect = reverse("login") + "?next=" + reverse(
            'posts:add_comment', args='1')
        self.assertRedirects(response, redirect)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый коммент1',
            ).exists()
        )
