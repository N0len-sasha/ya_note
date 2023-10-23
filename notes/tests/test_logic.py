from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils.text import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.author = User.objects.create(username='author')
        cls.non_author = User.objects.create(username='non_author')
        cls.anonim = User.objects.create(username='anonimuser')
        cls.anonim = Client()
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        title = 'title'
        cls.form_data = {'title': title,
                         'text': 'text',
                         'slug': slugify(title)}
        cls.same_slug = {'title': 'title2',
                         'text': 'text',
                         'slug': slugify(title)}
        cls.no_slug_data = {'title': 'title2',
                            'text': 'text'}

    def test_add_availabity(self):
        '''Проверка добавления заметки не/залогиненым пользователем'''

        statuses = (
            (self.anonim, 0),
            (self.auth_user, 1),
        )

        for name, status in statuses:
            name.post(reverse('notes:add'), data=self.form_data)
            notes_count = Note.objects.count()
            self.assertEqual(notes_count, status)

    def test_same_slug(self):
        '''Проверка предупрежения при том же slug'''

        self.client.force_login(self.user)
        self.client.post(reverse('notes:add'), data=self.form_data)
        response = self.client.post(reverse('notes:add'), data=self.same_slug)
        self.assertFormError(response, form='form',
                             field='slug',
                             errors=[f'{self.same_slug["slug"]}{WARNING}'])

    def test_add_no_slug(self):
        '''Проверка создания заметки без slug'''

        self.client.force_login(self.user)
        self.client.post(reverse('notes:add'), data=self.no_slug_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        '''Автор может удалить заметку'''

        self.client.force_login(self.author)
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author
        )
        delete_url = reverse('notes:delete', args=[note.slug])
        self.client.delete(delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note(self):
        '''Не автор не может удалить заметку'''

        self.client.force_login(self.non_author)
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author
        )
        delete_url = reverse('notes:delete', args=[note.slug])
        self.client.delete(delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNotePermissions(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author', password='password')
        cls.non_author = User.objects.create(username='non_author', password='password')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_user_can_edit_own_note(self):
        self.client.force_login(self.author)
        edit_url = reverse('notes:edit', args=(self.note.slug,))

        self.client.post(edit_url, data={'title': 'Новый заголовок',
                                         'text': 'Новый текст'})

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Новый заголовок')
        self.assertEqual(self.note.text, 'Новый текст')

    def test_user_cannot_edit_other_user_note(self):
        self.client.force_login(self.non_author)
        edit_url = reverse('notes:edit', args=(self.note.slug,))

        self.client.post(edit_url, data={'title': 'Новый заголовок',
                                                    'text': 'Новый текст'})
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Заголовок')
        self.assertEqual(self.note.text, 'Текст')
