import pytest
from unittest.mock import patch, MagicMock
from src.api.note_service import (
    get_notes,
    get_note_by_id,
    create_note,
    update_note,
    delete_note,
)
from src.models.note import Note


@patch("src.api.note_service.NotesDB.get_notes_for_user")
def test_get_notes(mock_get_notes_for_user):
    """
    GIVEN an author ID, page, and page size
    WHEN get_notes is called
    THEN the notes are returned
    """
    mock_notes = [MagicMock(spec=Note) for _ in range(3)]
    mock_get_notes_for_user.return_value = mock_notes

    author_id = 1
    page = 1
    page_size = 10
    notes = get_notes(author_id, page, page_size)

    assert notes == mock_notes
    mock_get_notes_for_user.assert_called_once_with(author_id, page, page_size)


@patch("src.api.note_service.NotesDB.get_note_by_id")
def test_get_note_by_id_public(mock_get_note_by_id):
    """
    GIVEN an author ID and note ID
    WHEN get_note_by_id is called for a public note
    THEN the note is returned
    """
    mock_note = MagicMock(spec=Note)
    mock_note.is_public = True
    mock_note.author_id = 2
    mock_get_note_by_id.return_value = mock_note

    author_id = 1
    note_id = 1
    note = get_note_by_id(author_id, note_id)

    assert note == mock_note
    mock_get_note_by_id.assert_called_once_with(note_id)


@patch("src.api.note_service.NotesDB.get_note_by_id")
def test_get_note_by_id_private(mock_get_note_by_id):
    """
    GIVEN an author ID and note ID
    WHEN get_note_by_id is called for a private note by the author
    THEN the note is returned
    """
    mock_note = MagicMock(spec=Note)
    mock_note.is_public = False
    mock_note.author_id = 1
    mock_get_note_by_id.return_value = mock_note

    author_id = 1
    note_id = 1
    note = get_note_by_id(author_id, note_id)

    assert note == mock_note
    mock_get_note_by_id.assert_called_once_with(note_id)


@patch("src.api.note_service.NotesDB.get_note_by_id")
def test_get_note_by_id_not_author(mock_get_note_by_id):
    """
    GIVEN an author ID and note ID
    WHEN get_note_by_id is called for a private note by a different author
    THEN None is returned
    """
    mock_note = MagicMock(spec=Note)
    mock_note.is_public = False
    mock_note.author_id = 2
    mock_get_note_by_id.return_value = mock_note

    author_id = 1
    note_id = 1
    note = get_note_by_id(author_id, note_id)

    assert note is None
    mock_get_note_by_id.assert_called_once_with(note_id)


@patch("src.api.note_service.NotesDB.create_note")
def test_create_note(mock_create_note):
    """
    GIVEN note details
    WHEN create_note is called
    THEN a new note is created and returned
    """
    mock_note = MagicMock(spec=Note)
    mock_create_note.return_value = mock_note

    note_title = "Test Note"
    note_text = "This is a test note."
    author_id = 1
    is_public = True
    note = create_note(note_title, note_text, author_id, is_public)

    assert note == mock_note
    mock_create_note.assert_called_once_with(
        note_title, note_text, author_id, is_public
    )


@patch("src.api.note_service.NotesDB.update_note")
def test_update_note(mock_update_note):
    """
    GIVEN note details
    WHEN update_note is called
    THEN the note is updated and returned
    """
    mock_note = MagicMock(spec=Note)
    mock_update_note.return_value = mock_note

    note_id = 1
    note_title = "Updated Note"
    note_text = "This is an updated test note."
    author_id = 1
    is_public = True
    note = update_note(note_id, note_title, note_text, author_id, is_public)

    assert note == mock_note
    mock_update_note.assert_called_once_with(
        note_id, note_title, note_text, author_id, is_public
    )


@patch("src.api.note_service.NotesDB.delete_note")
def test_delete_note(mock_delete_note):
    """
    GIVEN an author ID and note ID
    WHEN delete_note is called
    THEN the note is deleted and True is returned
    """
    mock_delete_note.return_value = True

    author_id = 1
    note_id = 1
    result = delete_note(author_id, note_id)

    assert result is True
    mock_delete_note.assert_called_once_with(author_id, note_id)
