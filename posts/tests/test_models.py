from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create()
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Запись',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'text': 'Содержание записи',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_len_post_text(self):
        post = PostModelTest.post
        expected_post = post.text[:15]
        self.assertEqual(expected_post, str(post.text))

    def test_object_name_is_title_field(self):
        post = PostModelTest.post
        expected_name = (f'{post.author.username}, '
                         f'{post.group}, {post.pub_date}, {post.text[:15]}')
        self.assertEqual(expected_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create()

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальныей ключ',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Дайте короткое название группы',
            'slug': ('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания')
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
