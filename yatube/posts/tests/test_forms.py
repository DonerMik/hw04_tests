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
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=form_date, follow=True)
        self.assertEqual(post_count + 1, Post.objects.count())

    def test_create_post_change_post(self):
        post_id = PostsFormTest.post.pk
        form_date = {
            'text': 'Текст из формы'}

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_date, follow=True)
        self.assertEqual(response.context['post'].text, 'Текст из формы')

