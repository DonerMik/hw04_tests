from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Tестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовая группа',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        test_title = post.text[:15]
        self.assertEqual(test_title, 'Текстовая группа'[:15], 'хуйня какая')
