from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_user = Client()
        self.templates_objects_name = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }

    def test_urls_uses_correct_templates(self):
        """Проверка, что URL'ы используют соответствующие шаблоны."""
        for template, address in self.templates_objects_name.items():
            with self.subTest(address=address):
                response = self.guest_user.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_disered_location(self):
        """Страницы приложения about доступны любому пользователю."""
        for about_pages in self.templates_objects_name.values():
            with self.subTest(about_pages=about_pages):
                response = self.guest_user.get(about_pages)
                self.assertEqual(response.status_code, HTTPStatus.OK)
