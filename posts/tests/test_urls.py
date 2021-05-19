from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

GROUP_TITLE = 'Новое сообщество'
GROUP_SLUG = 'test_group'
USER_NAME = 'Asp1n'
HOME_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:new_post')
GROUP_URL = reverse('posts:group_posts', args=(GROUP_SLUG,))
PROFILE_URL = reverse('posts:profile', args=(USER_NAME,))
FOLLOW = reverse('posts:follow_index')
FOLLOWING = reverse('posts:profile_follow', args=(USER_NAME,))
UNFOLLOWING = reverse('posts:profile_unfollow', args=(USER_NAME,))
REDIRECT_URL = reverse('login') + '?next='
REDIRECT_NEW_POST = f'{REDIRECT_URL},{NEW_POST_URL}'
REDIRECT_FOLLOWING = f'{REDIRECT_URL}, {FOLLOWING}'
REDIRECT_UNFOLLOWING = f'{REDIRECT_URL}, {UNFOLLOWING}'
ERROR404 = 'AJSFjasbf2i3h2930-1-=2rkamvlzxvnsjbf_ABSJBFAKS'
FOUND = HTTPStatus.FOUND
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_2 = User.objects.create_user(username='Asp1n_2')
        cls.user = User.objects.create(username=USER_NAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            text='test',
            author=cls.user,
        )
        cls.POST_URL = reverse(
            'posts:post',
            kwargs={'username': cls.user, 'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'username': cls.user, 'post_id': cls.post.id})
        cls.COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={'username': cls.user, 'post_id': cls.post.id})
        cls.REDIRECT_POST_EDIT = f'{REDIRECT_URL},{cls.POST_EDIT_URL}'
        cls.REDIRECT_COMMENT = f'{REDIRECT_URL}, {cls.COMMENT_URL}'
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.not_author = Client()
        cls.authorized_client.force_login(cls.user)
        cls.not_author.force_login(cls.user_2)

    def test_accesses_url(self):
        guest = self.guest_client
        author = self.authorized_client
        another = self.not_author
        urls_names = [
            [HOME_URL, guest, OK],
            [GROUP_URL, guest, OK],
            [PROFILE_URL, guest, OK],
            [self.POST_URL, guest, OK],
            [REDIRECT_NEW_POST, guest, OK],
            [self.REDIRECT_POST_EDIT, guest, OK],
            [self.REDIRECT_COMMENT, guest, OK],
            [REDIRECT_FOLLOWING, guest, OK],
            [REDIRECT_UNFOLLOWING, guest, OK],
            [NEW_POST_URL, guest, FOUND],
            [self.POST_EDIT_URL, guest, FOUND],
            [self.POST_EDIT_URL, another, FOUND],
            [NEW_POST_URL, author, OK],
            [self.COMMENT_URL, author, FOUND],
            [FOLLOW, author, OK],
            [self.POST_EDIT_URL, author, OK],
            [ERROR404, guest, NOT_FOUND]
        ]
        for url, user, code in urls_names:
            with self.subTest(url=url):
                self.assertEqual(user.get(url).status_code, code)

    def test_accesses_redirects(self):
        guest = self.guest_client
        urls_names = [
            [self.POST_EDIT_URL,
             guest,
             (REDIRECT_URL + self.POST_EDIT_URL)],
            [NEW_POST_URL,
             guest,
             (REDIRECT_URL + NEW_POST_URL)],
            [self.POST_EDIT_URL, self.not_author, self.POST_URL],
            [self.COMMENT_URL,
             guest,
             REDIRECT_URL + self.COMMENT_URL],
            [FOLLOWING, guest, REDIRECT_URL + FOLLOWING],
            [UNFOLLOWING, guest, REDIRECT_URL + UNFOLLOWING],
        ]
        for url, client, redirected in urls_names:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirected)

    def test_urls_uses_correct_template(self):
        template_url_name = [
            ['index.html', HOME_URL],
            ['group.html', GROUP_URL],
            ['new.html', NEW_POST_URL],
            ['profile.html', PROFILE_URL],
            ['post.html', self.POST_URL],
            ['new.html', self.POST_EDIT_URL],
            ['follow.html', FOLLOW]
        ]

        for template, url in template_url_name:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url), template)
