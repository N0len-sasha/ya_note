from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from notes.models import Note


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')
        title = 'Заголовок'
        cls.note = Note.objects.create(title=title,
                                       text='Текст',
                                       author=cls.user,
                                       slug=slugify(title))

    def test_home_page(self):
        '''Тестирование доступности главной страницы анонимом'''

        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_user_add_done_notes_availability(self):
        '''Тестирование доступности 3ех страниц логиненому'''

        self.client.force_login(self.user)
        for name in ('notes:add', 'notes:success', 'notes:list'):
            with self.subTest(user=self.user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_access_by_author_and_non_author(self):
        users = [self.user, self.reader]
        actions = {
            'view': 'notes:detail',
            'edit': 'notes:edit',
            'delete': 'notes:delete',
        }

        for user in users:
            self.client.force_login(user)
            for action, url_name in actions.items():
                with self.subTest(user=user, action=action):
                    url = reverse(url_name, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK if user == self.user
                                     else HTTPStatus.NOT_FOUND)

    def test_redirect_delete_edit_detail_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_add_success_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:add', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_users_pages_availability(self):
        urls = (
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
