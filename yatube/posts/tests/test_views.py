from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='den')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        post_id = PostViewsTests.post.pk
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list',
                        kwargs={'slug': PostViewsTests.group.slug}),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': str(post_id)})
        }

        for template, reverse_name in templates_pages_names.items():
            response = self.guest_client.get(reverse_name)
            self.assertTemplateUsed(response, template)

    def test_page_post_create_uses_template(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_page_post_edit_uses_template(self):
        post_id = PostViewsTests.post.pk
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': post_id}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_detail_contains_one_post(self):
        post_id = PostViewsTests.post.pk
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id}))
        post_detail = response.context['post']
        post_pk = post_detail.pk
        self.assertEqual(post_id, post_pk)

    def test_edit_page_show_correct_context(self):
        post_id = PostViewsTests.post.pk
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context соотв. ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_create_page_show_correct_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        # Проверяем, что типы полей формы в словаре context соотв. ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_page_list_is_1(self):
        # Удостоверимся, что на страницу со списком заданий передаётся
        # ожидаемое количество объектов
        response = self.authorized_client.get(reverse('posts:index'))
        object_all = response.context['page_obj']
        self.assertEqual(len(object_all), 1)

    def test_group_page_list_is_1(self):
        # Удостоверимся, что на страницу со списком заданий передаётся
        # ожидаемое количество объектов
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTests.post.group.slug}))
        object_all = response.context['page_obj']
        self.assertEqual(len(object_all), 1)

    def test_profile_page_list_is_1(self):
        # Удостоверимся, что на страницу со списком заданий передаётся
        # ожидаемое количество объектов
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostViewsTests.post.author}))
        object_all = response.context['page_obj']
        self.assertEqual(len(object_all), 1)

    def test_no_have_other_group_list(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug2'}))
        object_all = response.context['page_obj']
        self.assertEqual(len(object_all), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='test-slug',
            slug='test-slug',
            description='Tестовое описание')

        list_posts_objects = [Post(
            author=cls.user,
            text=f'Тест текст {post}',
            group=cls.group) for post in range(1, 14)
        ]

        cls.creater_post = Post.objects.bulk_create(list_posts_objects)
        cls.second_page_post = 3

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_index_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), settings.COUNT_IN_PAGES)

    def test_second_page_index_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         PaginatorViewsTest.second_page_post)

    def test_first_page_group_list_contains_ten_records(self):
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']),
                         settings.COUNT_IN_PAGES)

    def test_second_page_group_list_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         PaginatorViewsTest.second_page_post)

    def test_first_page_profile_contains_ten_records(self):
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']),
                         settings.COUNT_IN_PAGES)

    def test_second_page_profile_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         PaginatorViewsTest.second_page_post)
