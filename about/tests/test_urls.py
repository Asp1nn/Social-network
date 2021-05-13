from django.test import TestCase, Client


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        url_name = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for url, code in url_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_about_url_uses_correct_template(self):
        template_url_name = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in template_url_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
