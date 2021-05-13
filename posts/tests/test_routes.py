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
        ]
        for url, route in urls_routes_names:
            self.assertEqual(url, route)
