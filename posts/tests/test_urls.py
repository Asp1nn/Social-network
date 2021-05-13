from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

GROUP_TITLE = 'Новое сообщество'
GROUP_SLUG = 'test_group'
USER_NAME = 'Asp1n'
HOME_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:new_post')
GROUP_URL = reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USER_NAME})
REDIRECT_URL = reverse('login') + '?next='
ERROR404 = 'not_found'


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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.not_author = Client()
        self.authorized_client.force_login(self.user)
        self.not_author.force_login(self.user_2)

    def test_accesses_url(self):
        urls_names = [
            [HOME_URL, self.guest_client, HTTPStatus.OK],
            [GROUP_URL, self.guest_client, HTTPStatus.OK],
            [PROFILE_URL, self.guest_client, HTTPStatus.OK],
            [self.POST_URL, self.guest_client, HTTPStatus.OK],
            [REDIRECT_URL + NEW_POST_URL,
             self.guest_client,
             HTTPStatus.OK],
            [REDIRECT_URL + self.POST_EDIT_URL,
             self.guest_client,
             HTTPStatus.OK],
            [NEW_POST_URL, self.guest_client, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.guest_client, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.not_author, HTTPStatus.FOUND],
            [NEW_POST_URL, self.authorized_client, HTTPStatus.OK],
            [self.POST_EDIT_URL, self.authorized_client, HTTPStatus.OK],
            [ERROR404, self.guest_client, HTTPStatus.NOT_FOUND]
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
            [self.POST_EDIT_URL, self.not_author, self.POST_URL]
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
            ['new.html', self.POST_EDIT_URL]
        ]

        for template, url in template_url_name:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
