import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Group


GROUP_TITLE = 'Новое сообщество'
GROUP_SLUG = 'test_group'
USER_NAME = 'Asp1n'
POST_TEXT = 'Тестовая запись'
HOME_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:new_post')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B')


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=USER_NAME)
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
        )
        cls.POST_URL = reverse(
            'posts:post',
            kwargs={'username': cls.user, 'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'username': cls.user, 'post_id': cls.post.id})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_creat_new_post(self):
        post_count = Post.objects.count()
        posts_id = [post.pk for post in Post.objects.all()]
        form_data = {
            'text': 'test_text',
            'group': self.group.id,
            'image': self.uploaded
        }
        response_1 = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        posts_new_id = [post.pk for post in Post.objects.all()]
        new_post_id = list(set(posts_new_id) - set(posts_id))
        self.assertEqual(len(new_post_id), 1)
        post = Post.objects.get(id=new_post_id[0])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response_1, HOME_URL)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(image=post.image).exists()
        )

    def test_change_post(self):
        new_group = Group.objects.create(title='new_group', slug='new_group')
        form_data = {
            'text': 'new_text',
            'group': new_group.id,
        }
        response = self.authorized_client.post(self.POST_EDIT_URL,
                                               data=form_data,
                                               follow=True
                                               )
        post = response.context['post']
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.group.id, new_group.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_URL)

    def test_new_and_edit_page_show_correct_context_in_form(self):
        url_form_field = [
            [NEW_POST_URL,
             {'group': forms.fields.ChoiceField,
              'text': forms.fields.CharField}],
            [self.POST_EDIT_URL,
             {'group': forms.fields.ChoiceField,
              'text': forms.fields.CharField}],
        ]
        for url, values in url_form_field:
            for value, expected in values.items():
                with self.subTest(value=value):
                    response = self.authorized_client.get(url)
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)
