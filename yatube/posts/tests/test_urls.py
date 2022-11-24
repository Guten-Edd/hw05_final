from django.test import TestCase, Client
from http import HTTPStatus
from posts.models import Post, Group, User
from django.core.cache import cache


adress_home = '/'
adress_group = '/group/test-slug/'
adress_profile = '/profile/TestUser/'
adress_post = '/posts/1/'
adress_post_create = '/create/'
adress_post_edit = '/posts/1/edit/'
adress_unexpected_page = '/unexpected_page/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='TestGroupdesc',
        )
        # Создадим запись в БД для проверки доступности адреса post/test-slug/
        cls.posr = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон. для """
        # Шаблоны по адресам

        templates_url_names = {
            adress_home: 'posts/index.html',
            adress_group: 'posts/group_list.html',
            adress_profile: 'posts/profile.html',
            adress_post: 'posts/post_detail.html',
            adress_post_create: 'posts/create_post.html',
            adress_post_edit: 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем общедоступные страницы
    def test_index_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(adress_home)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'index.html недоступен')

    def test_group_list_url_exists_at_desired_location(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get(adress_group)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         '/group/<slug:slug>/ недоступен')

    def test_user_profile_url_exists_at_desired_location(self):
        """Страница /profile/<str:username>/ доступна любому пользователю."""
        response = self.guest_client.get(adress_profile)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'profile/<str:username>/ недоступен')

    def test_posts_id_url_exists_at_desired_location(self):
        """Страница /posts/<int:post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(adress_post)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         '/posts/<int:post_id>/ недоступен')

    # Проверяем что запрос к несуществующей странице вернёт ошибку 404.
    def test_unexpected_page_url_Not_exists_at_desired_location(self):
        """Страница /unexpected_page/ Недоступна."""
        response = self.guest_client.get(adress_unexpected_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(adress_post_create)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         '/create/ недоступен')

    # Проверяем доступность страниц для автора
    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/<int:post_id>/edit/ доступна авторизованному"""
        response = self.authorized_client.get(adress_post_edit)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         '/posts/<int:post_id>/edit/ недоступен')
