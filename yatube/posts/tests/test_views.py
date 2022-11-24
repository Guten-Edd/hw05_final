from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group, User, Follow
from posts.views import POSTS_PER_PAGE
import tempfile
import shutil
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='TestGroupdesc',
        )
        cls.user = User.objects.create_user(username='TestUser')
        Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': 'TestUser'})):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image.name

        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_cache_index_page(self):
        """Кеш на странице index работает корректно"""
        cache_post = Post.objects.create(
            author=PostPagesTests.user,
            text='Текст для кеша',
            group=PostPagesTests.group,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        objects_before_deleting = response.context

        cache_post.delete()

        objects_after_deleting = response.context
        self.assertEqual(objects_before_deleting, objects_after_deleting)

        cache.clear()

        response = self.authorized_client.get(reverse('posts:index'))
        objects_after_cashe = response.context
        self.assertNotEqual(objects_after_cashe, objects_after_deleting)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_title = first_object.group.title
        post_group_description = first_object.group.description
        post_image_0 = first_object.image.name
        post_author_0 = first_object.author.username

        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_group_title, 'Тестовая группа')
        self.assertEqual(post_group_description, 'TestGroupdesc')
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'TestUser'}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image.name

        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        context = response.context['post']
        post_text = context.text
        post_author = context.author.username
        post_group = context.group.title
        post_image = context.image.name

        self.assertEqual(post_text, 'Текст')
        self.assertEqual(post_author, 'TestUser')
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}
        ))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)


NUMBER_OF_TEST_POSTS = 13  # количество постов
NUMBER_OF_TEST_POSTS_SECOND_PAGE = NUMBER_OF_TEST_POSTS - POSTS_PER_PAGE


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора"""
    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='TestGroupDesc',
        )
        cls.user = User.objects.create_user(username='TestUserPaginator')
        cls.post_list = []

        for i in range(NUMBER_OF_TEST_POSTS):
            cls.post_list.append(Post(
                text=f'Тестовый текст {i}',
                group=cls.group,
                author=cls.user)
            )

        Post.objects.bulk_create(cls.post_list)

        def setUp(self):
            self.authorized_client = Client()
            self.authorized_client.force_login(self.user)
            cache.clear()

    def test_index_first_page_contains_ten_records(self):
        """Тестирование первой страницы index на количество постов"""
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно POSTS_PER_PAGE.
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_index_second_page_contains_three_records(self):
        """Тестирование второй страницы index на количество постов"""

        # Проверка: на второй странице должно быть
        # NUMBER_OF_TEST_POSTS_SECOND_PAGE.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         NUMBER_OF_TEST_POSTS_SECOND_PAGE)

    def test_group_list_first_page_contains_ten_records(self):
        """Тестирование первой страницы group_list на количество постов"""

        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        # Проверка: количество постов на первой странице равно POSTS_PER_PAGE.
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_group_list_second_page_contains_three_records(self):
        """Тестирование второй страницы group_list на количество постов"""

        # Проверка: на второй странице должно быть
        # NUMBER_OF_TEST_POSTS_SECOND_PAGE.
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         NUMBER_OF_TEST_POSTS_SECOND_PAGE)

    def test_profile_first_page_contains_ten_records(self):
        """Тестирование первой страницы profile на количество постов"""

        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'TestUserPaginator'}
        ))
        # Проверка: количество постов на первой странице равно POSTS_PER_PAGE.
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_profile_second_page_contains_three_records(self):
        """Тестирование второй страницы profile на количество постов"""

        # Проверка: на второй странице должно быть
        # NUMBER_OF_TEST_POSTS_SECOND_PAGE.
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'TestUserPaginator'}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         NUMBER_OF_TEST_POSTS_SECOND_PAGE)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username="test-author")
        cls.follower = User.objects.create_user(username='follower')
        cls.not_follower = User.objects.create_user(username='not_follower')

    def setUp(self):
        self.test_user_client = Client()
        self.test_user_client.force_login(FollowTests.test_user)
        self.follower_client = Client()
        self.follower_client.force_login(FollowTests.follower)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(FollowTests.not_follower)

    def test_user_follow_another_user(self):
        '''Авторизованный пользователь может подписаться
        на другого пользователя'''
        count_follow = Follow.objects.count()
        self.test_user_client.post(reverse('posts:profile_follow',
                                   kwargs={'username': self.follower}))
        self.assertEqual(Follow.objects.count(), count_follow + 1)

    def test_follow_index_show_correct_post(self):
        """Новая запись пользователя появляется в ленте тех, кто
        на него подписан и не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(
            author=self.test_user,
            user=self.follower
        )
        Post.objects.create(
            text='test_one_post',
            author=self.test_user
        )
        response_not_follower = self.not_follower_client.get(
            reverse('posts:follow_index')
        )
        before_not_follower = len(response_not_follower.context["page_obj"])
        response_follower = self.follower_client.get(
            reverse('posts:follow_index')
        )
        before_follower = len(response_follower.context["page_obj"])
        Post.objects.create(
            text='test_one_post',
            author=self.test_user)
        after_not_follower = len(response_not_follower.context["page_obj"])
        self.assertEqual(before_not_follower, after_not_follower)
        after_follower = len(response_follower.context["page_obj"])
        self.assertEqual(before_follower, after_follower)

    def test_user_unfollow_another_user(self):
        '''Авторизованный пользователь может отписаться
        от другого пользователя'''
        self.test_user_client.post(reverse('posts:profile_follow',
                                   kwargs={'username': self.follower}))
        count_follow = Follow.objects.count()
        self.test_user_client.post(reverse('posts:profile_unfollow',
                                   kwargs={'username': self.follower}))
        self.assertEqual(Follow.objects.count(), count_follow - 1)
