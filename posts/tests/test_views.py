import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts import setting
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
FOLLOWING = reverse('posts:profile_follow', args=(USER_NAME,))
UNFOLLOWING = reverse('posts:profile_unfollow', args=(USER_NAME,))
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
            kwargs={'username': cls.user, 'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'username': cls.user, 'post_id': cls.post.id})
        cls.COMMENT = reverse(
            'posts:add_comment',
            kwargs={'username': cls.user, 'post_id': cls.post.id})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)
        cache.clear()

    def test_pages_show_correct_context(self):
        items = [
            [HOME_URL, 'page'],
            [PROFILE_URL, 'page'],
            [GROUP_URL, 'page'],
            [self.POST_URL, 'post']
        ]
        for url, context in items:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
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

    def test_cache(self):
        self.authorized_client.get(reverse('posts:index'))
        key = make_template_fragment_key('index_page')
        self.assertIsNotNone(cache.get(key))

    def test_following_and_unfollowing(self):
        chek_follower = Follow.objects.count()
        self.authorized_client_2.get(FOLLOWING)
        chek_follower_2 = Follow.objects.count()
        self.assertEqual(chek_follower_2, chek_follower + 1)
        self.authorized_client_2.get(UNFOLLOWING)
        chek_follower_3 = Follow.objects.count()
        self.assertEqual(chek_follower_3, chek_follower)

    def test_new_post_appears_for_subscribers(self):
        self.authorized_client_2.get(FOLLOWING)
        form_data = {
            'text': 'new_post',
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertIn(
            response.context['post'],
            self.authorized_client_2.get(FOLLOW).context['page'])
        self.assertNotIn(
            response.context['post'],
            self.authorized_client.get(FOLLOW).context['page'])

    def test_only_auth_user_can_comment_post(self):
        self.assertRedirects(
            self.guest_client.get(self.COMMENT), REDIRECT_URL + self.COMMENT)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='name')
        cls.client = Client()
        cls.post_count_three = 3
        cls.check_post_count = setting.POST_COUNT + cls.post_count_three
        for _ in range(cls.check_post_count):
            cls.post = Post.objects.create(
                text='Тестовая запись',
                author=cls.user)

    def test_first_page_contains_no_more_than_ten_records(self):
        response = self.client.get(HOME_URL)
        self.assertEqual(
            len(response.context.get('page')),
            setting.POST_COUNT
        )

    def test_second_page_contains_three_records(self):
        response = self.client.get(HOME_URL + '?page=2')
        self.assertEqual(
            len(response.context.get('page')),
            self.post_count_three
        )
