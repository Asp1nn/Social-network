import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache, caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.settings import POSTS_NUMBER
from posts.models import Group, Post, User, Follow


GROUP_TITLE = 'Новое сообщество'
GROUP_SLUG = 'test_group'
GROUP_TEXT = 'description'
USER_NAME = 'Asp1n'
USER_NAME_2 = 'new_user'
POST_TEXT = 'Тестовая запись'
HOME_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:new_post')
GROUP_URL = reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USER_NAME})
REDIRECT_URL = reverse('login') + '?next='
FOLLOW = reverse('posts:follow_index')
FOLLOWING_ON_USER = reverse('posts:profile_follow', args=(USER_NAME,))
FOLLOWING_ON_USER_2 = reverse('posts:profile_follow', args=(USER_NAME_2,))
UNFOLLOWING_ON_USER = reverse('posts:profile_unfollow', args=(USER_NAME,))
UNFOLLOWING_ON_USER_2 = reverse('posts:profile_unfollow', args=(USER_NAME_2,))
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B')


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=USER_NAME)
        cls.user_2 = User.objects.create(username=USER_NAME_2)
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_TEXT
        )
        cls.test_group = Group.objects.create(
            title='new_group',
            slug='new_group')
        cls.GROUP_URL_2 = reverse(
            'posts:group_posts', kwargs={'slug': cls.test_group.slug})
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.POST_URL = reverse(
            'posts:post',
            kwargs={'username': cls.user.username, 'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'username': cls.user.username, 'post_id': cls.post.id})
        cls.COMMENT = reverse(
            'posts:add_comment',
            kwargs={'username': cls.user.username, 'post_id': cls.post.id})
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
        Follow.objects.create(
            user=cls.user_2,
            author=cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()

    def test_pages_show_correct_context(self):
        items = [
            [HOME_URL, 'page'],
            [PROFILE_URL, 'page'],
            [GROUP_URL, 'page'],
            [FOLLOW, 'page'],
            [self.POST_URL, 'post']
        ]
        for url, context in items:
            with self.subTest(url=url):
                response = self.authorized_client_2.get(url)
                if context != 'post':
                    self.assertEqual(len(response.context[context]), 1)
                    post = response.context[context][0]
                else:
                    post = response.context[context]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group.id, self.post.group.id)
                self.assertEqual(post.image, self.post.image)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(GROUP_URL)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_new_post_in_the_wrong_group(self):
        self.assertNotIn(
            self.post,
            self.authorized_client.get(self.GROUP_URL_2).context['page'])

    def test_cache_page_index(self):
        response_1 = self.guest_client.get(HOME_URL)
        Post.objects.all().delete()
        self.assertEqual(
            self.guest_client.get(HOME_URL).content, response_1.content
        )
        caches['default'].clear()
        response_2 = self.guest_client.get(HOME_URL)
        self.assertNotEqual(response_2.content, response_1.content)

    def test_unfollowing(self):
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_2,
                author=self.user).exists()
        )
        self.authorized_client_2.get(UNFOLLOWING_ON_USER)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_2,
                author=self.user).exists()
        )

    def test_following(self):
        self.authorized_client.get(FOLLOWING_ON_USER_2)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_2,
                author=self.user).exists()
        )

    def test_post_do_not_appears_for_not_a_subscribers(self):
        self.assertNotIn(
            self.post,
            self.authorized_client.get(FOLLOW).context['page'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='name')
        cls.client = Client()
        cls.post_count = 3
        check_post_count = POSTS_NUMBER + cls.post_count
        for _ in range(check_post_count):
            cls.post = Post.objects.create(
                text='Тестовая запись',
                author=cls.user)

    def test_first_page_contains_quantity_records_posts(self):
        response = self.client.get(HOME_URL)
        self.assertEqual(
            len(response.context.get('page')),
            POSTS_NUMBER
        )

    def test_second_page_contains_quantity_records(self):
        response = self.client.get(HOME_URL + '?page=2')
        self.assertEqual(
            len(response.context.get('page')),
            self.post_count
        )
