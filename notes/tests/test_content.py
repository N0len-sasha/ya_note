from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        title = 'Заголовок'
        cls.user = User.objects.create(username='testuser')
        cls.another_user = User.objects.create(username='anotheruser')
        cls.note = Note.objects.create(title='Новость',
                                       text='Просто текст.',
                                       author=cls.user,
                                       slug=slugify(title))
        cls.note2 = Note.objects.create(title='Новость 2',
                                        text='Просто текст.',
                                        author=cls.another_user,
                                        slug=slugify(title))

    def test_note_in_context(self):
        '''Проверка вхождения заметки в контекст'''

        self.client.force_login(self.user)
        response = self.client.get(self.HOME_URL)
        notes = response.context['notes_list']
        self.assertIn(self.note, notes)

    def test_notes_doesnt_mix(self):
        '''Тест на "несмешивание" заметок разных пользователей'''

        self.client.force_login(self.user)
        response = self.client.get(self.HOME_URL)
        notes_user = response.context['notes_list']
        self.assertNotIn(self.note2, notes_user)

    def test_sent_form_in_context(self):
        '''Тест передачи формы в контекст'''

        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )

        self.client.force_login(self.user)

        for url, args in urls:
            response = self.client.get(reverse(url, args=args))
            self.assertIn('form', response.context)
