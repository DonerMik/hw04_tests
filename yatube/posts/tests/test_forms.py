from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostsFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='den')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
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

    def test_create_post(self):
        post_count = Post.objects.count()
        form_date = {
            'text': 'Текст из формы',
            'group': PostsFormTest.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_date, follow=True)
        self.assertEqual(post_count + 1, Post.objects.count())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_post = Post.objects.all()[0]
        new_post_text = new_post.text
        new_post_author = new_post.author.username
        new_post_group = new_post.group.pk
        self.assertEqual(new_post_text, form_date['text'])
        self.assertEqual(new_post_author, PostsFormTest.user.username)
        self.assertEqual(new_post_group, form_date['group'])

    def test_change_post(self):
        post_id = PostsFormTest.post.pk
        form_date = {
            'text': 'Измененный текст из формы',
            'group': PostsFormTest.group.pk
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_date, follow=True)
        change_post_text = response.context['post'].text
        self.assertEqual(change_post_text, form_date['text'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_client_no_create_post(self):
        post_count = Post.objects.count()
        form_date = {
            'text': 'Текст из формы',
            'group': PostsFormTest.group.pk
        }

        response = self.guest_client.post(
            reverse('posts:post_create'), data=form_date, follow=True)
        new_post_count = Post.objects.count()
        self.assertRedirects(response,
                             f"{reverse('users:login')}?next="
                             f"{reverse('posts:post_create')}")
        self.assertEqual(post_count, new_post_count)
