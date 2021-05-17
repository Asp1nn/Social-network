from django.test import TestCase
from django.urls import reverse


class RoutesTest(TestCase):
    def test_routes(self):
        author = 'Asp1n'
        slug = 'test_group'
        post_id = 1
        urls_routes_names = [
            [reverse('posts:index'), '/'],
            [reverse('posts:new_post'), '/new/'],
            [reverse(
                'posts:group_posts',
                args=[slug]),
             f'/group/{slug}/'],
            [reverse(
                'posts:profile',
                args=[author]),
             f'/{author}/'],
            [reverse(
                'posts:post',
                args=[author, post_id]),
             f'/{author}/{post_id}/'],
            [reverse(
                'posts:post_edit',
                args=[author, post_id]),
             f'/{author}/{post_id}/edit/'],
            [reverse(
                'posts:follow_index'),
                '/follow/'],
            [reverse(
                'posts:profile_follow',
                args=[author]),
             f'/{author}/follow/'],
            [reverse(
                'posts:profile_unfollow',
                args=[author]),
             f'/{author}/unfollow/'],
            [reverse(
                'posts:add_comment',
                args=[author, post_id]),
                f'/{author}/{post_id}/comment/']
        ]
        for url, route in urls_routes_names:
            self.assertEqual(url, route)
