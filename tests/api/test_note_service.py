import pytest
from unittest.mock import patch, MagicMock
from src.api.note_service import NoteService
from src.db import notes
from src.models.note import Note


@pytest.fixture
def mock_notes_db():
    return MagicMock(spec=notes)


@pytest.fixture
def note_service(mock_notes_db):
    return NoteService(mock_notes_db)


def test_get_notes(note_service, mock_notes_db):
    """
    GIVEN an author ID, page, and page size
    WHEN get_notes is called
    THEN the notes are returned
    """
    mock_notes = [MagicMock(spec=Note) for _ in range(3)]
    mock_notes_db.get_notes_for_user.return_value = mock_notes

    author_id = 1
    page = 1
    page_size = 10
    notes = note_service.get_notes(author_id, page, page_size)

    assert notes == mock_notes
    mock_notes_db.get_notes_for_user.assert_called_once_with(author_id, page, page_size)


def test_get_note_by_id_public(note_service, mock_notes_db):
    """
    GIVEN an author ID and note ID
    WHEN get_note_by_id is called for a public note
    THEN the note is returned
    """
    mock_note = MagicMock(spec=Note)
    mock_note.is_public = True
    mock_note.author_id = 2
    mock_notes_db.get_note_by_id.return_value = mock_note

    author_id = 1
    note_id = 1
    note = note_service.get_note_by_id(author_id, note_id)

    assert note == mock_note
    mock_notes_db.get_note_by_id.assert_called_once_with(note_id)


def test_get_note_by_id_private(note_service, mock_notes_db):
    """
    GIVEN an author ID and note ID
    WHEN get_note_by_id is called for a private note by the author
    THEN the note is returned
    """
    mock_note = MagicMock(spec=Note)
    mock_note.is_public = False
    mock_note.author_id = 1
    mock_notes_db.get_note_by_id.return_value = mock_note

    author_id = 1
    note_id = 1
    note = note_service.get_note_by_id(author_id, note_id)

    assert note == mock_note
    mock_notes_db.get_note_by_id.assert_called_once_with(note_id)


def test_get_note_by_id_not_author(note_service, mock_notes_db):
    """
    GIVEN an author ID and note ID
    WHEN get_note_by_id is called for a private note by a different author
    THEN None is returned
    """
    mock_note = MagicMock(spec=Note)
    mock_note.is_public = False
    mock_note.author_id = 2
    mock_notes_db.get_note_by_id.return_value = mock_note

    author_id = 1
    note_id = 1
    note = note_service.get_note_by_id(author_id, note_id)

    assert note is None
    mock_notes_db.get_note_by_id.assert_called_once_with(note_id)


def test_create_note(note_service, mock_notes_db):
    """
    GIVEN note details
    WHEN create_note is called
    THEN a new note is created and returned
    """
    mock_note = MagicMock(spec=Note)
    mock_notes_db.create_note.return_value = mock_note

    note_title = "Test Note"
    note_text = "This is a test note."
    author_id = 1
    is_public = True
    note = note_service.create_note(note_title, note_text, author_id, is_public)

    assert note == mock_note
    mock_notes_db.create_note.assert_called_once_with(
        note_title, note_text, author_id, is_public
    )


def test_update_note(note_service, mock_notes_db):
    """
    GIVEN note details
    WHEN update_note is called
    THEN the note is updated and returned
    """
    mock_note = MagicMock(spec=Note)
    mock_notes_db.update_note.return_value = mock_note

    note_id = 1
    note_title = "Updated Note"
    note_text = "This is an updated test note."
    author_id = 1
    is_public = True
    note = note_service.update_note(
        note_id, note_title, note_text, author_id, is_public
    )

    assert note == mock_note
    mock_notes_db.update_note.assert_called_once_with(
        note_id, note_title, note_text, author_id, is_public
    )


def test_delete_note(note_service, mock_notes_db):
    """
    GIVEN an author ID and note ID
    WHEN delete_note is called
    THEN the note is deleted and True is returned
    """
    mock_notes_db.delete_note.return_value = True

    author_id = 1
    note_id = 1
    result = note_service.delete_note(author_id, note_id)

    assert result is True
    mock_notes_db.delete_note.assert_called_once_with(author_id, note_id)
