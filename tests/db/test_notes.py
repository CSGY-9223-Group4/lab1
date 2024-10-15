from unittest.mock import patch, MagicMock

from sqlalchemy import Select, Tuple

from src.models.note import Note
from src.db.notes import (
    create_note,
    get_note_by_id,
    get_notes_for_user,
    update_note,
    delete_note,
)


@patch("src.db.notes.get_db")
def test_update_note_success(mock_get_db):
    """
    GIVEN a note ID, title, text, author ID, and public status
    WHEN update_note is called
    THEN the note is updated and returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_id = 1
    note_title = "Updated Title"
    note_text = "Updated Text"
    author_id = 1
    is_public = True

    db_note = Note(
        note_id=note_id,
        note_title="Old Title",
        note_text="Old Text",
        author_id=author_id,
        is_public=False,
    )
    mock_db.execute.return_value.scalar_one_or_none.return_value = db_note

    updated_note = update_note(note_id, note_title, note_text, author_id, is_public)

    assert updated_note is not None
    assert updated_note.note_title == note_title
    assert updated_note.note_text == note_text
    assert updated_note.is_public == is_public
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(db_note)


@patch("src.db.notes.get_db")
def test_update_note_does_not_exist(mock_get_db):
    """
    GIVEN a note ID, title, text, author ID, and public status
    WHEN update_note is called with a non-existent note ID
    THEN None is returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_id = 1
    note_title = "Updated Title"
    note_text = "Updated Text"
    author_id = 1
    is_public = True

    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    updated_note = update_note(note_id, note_title, note_text, author_id, is_public)

    assert updated_note is None
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


@patch("src.db.notes.get_db")
def test_update_note_not_found(mock_get_db):
    """
    GIVEN a note ID, title, text, author ID, and public status
    WHEN update_note is called with a non-existent note ID
    THEN None is returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_id = 1
    note_title = "Updated Title"
    note_text = "Updated Text"
    author_id = 1
    is_public = True

    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    updated_note = update_note(note_id, note_title, note_text, author_id, is_public)

    assert updated_note is None
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


@patch("src.db.notes.get_db")
def test_delete_note_success(mock_get_db):
    """
    GIVEN a note ID and author ID
    WHEN delete_note is called
    THEN the note is deleted and True is returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_id = 1
    author_id = 1

    mock_db.execute.return_value.rowcount = 1

    result = delete_note(author_id, note_id)

    assert result is True
    mock_db.commit.assert_called_once()


@patch("src.db.notes.get_db")
def test_delete_note_not_found(mock_get_db):
    """
    GIVEN a note ID and author ID
    WHEN delete_note is called with a non-existent note ID
    THEN False is returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_id = 1
    author_id = 1

    mock_db.execute.return_value.rowcount = 0

    result = delete_note(author_id, note_id)

    assert result is False
    mock_db.commit.assert_called_once()


@patch("src.db.notes.get_db")
def test_get_notes_by_author_id(mock_get_db):
    """
    GIVEN an author ID
    WHEN get_notes_by_author_id is called
    THEN the notes are returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    author_id = 1

    db_notes = [
        Note(
            note_id=1,
            note_title="Note 1",
            note_text="Text 1",
            author_id=author_id,
            is_public=True,
        ),
        Note(
            note_id=2,
            note_title="Note 2",
            note_text="Text 2",
            author_id=author_id,
            is_public=False,
        ),
    ]
    mock_db.execute.return_value.scalars.return_value.all.return_value = db_notes

    notes = get_notes_for_user(author_id)

    assert notes == db_notes
    mock_db.execute.assert_called_once()


@patch("src.db.notes.get_db")
def test_get_notes_for_user_default_pagination(mock_get_db):
    """
    GIVEN an author ID
    WHEN get_notes_for_user is called with default pagination
    THEN the notes are returned with the correct offset and limit
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    author_id = 1
    page = 1
    page_size = 10

    db_notes = [
        Note(
            note_id=1,
            note_title="Note 1",
            note_text="Text 1",
            author_id=author_id,
            is_public=True,
        ),
        Note(
            note_id=2,
            note_title="Note 2",
            note_text="Text 2",
            author_id=author_id,
            is_public=False,
        ),
    ]
    mock_db.execute.return_value.scalars.return_value.all.return_value = db_notes

    notes = get_notes_for_user(author_id, page=page, page_size=page_size)

    assert notes == db_notes
    mock_db.execute.assert_called_once()
    args, _ = mock_db.execute.call_args
    query = args[0]
    assert query._limit == page_size
    assert query._offset == (page - 1) * page_size


@patch("src.db.notes.get_db")
def test_get_notes_for_user_custom_pagination(mock_get_db):
    """
    GIVEN an author ID
    WHEN get_notes_for_user is called with custom pagination
    THEN the notes are returned with the correct offset and limit
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    author_id = 1
    page = 2
    page_size = 5

    db_notes = [
        Note(
            note_id=3,
            note_title="Note 3",
            note_text="Text 3",
            author_id=author_id,
            is_public=True,
        ),
        Note(
            note_id=4,
            note_title="Note 4",
            note_text="Text 4",
            author_id=author_id,
            is_public=False,
        ),
    ]
    mock_db.execute.return_value.scalars.return_value.all.return_value = db_notes

    notes = get_notes_for_user(author_id, page=page, page_size=page_size)

    assert notes == db_notes
    mock_db.execute.assert_called_once()
    args, _ = mock_db.execute.call_args
    query = args[0]
    assert query._limit == page_size
    assert query._offset == (page - 1) * page_size


@patch("src.db.notes.get_db")
def test_get_note_by_id(mock_get_db):
    """
    GIVEN a note ID
    WHEN get_note_by_id is called
    THEN the note is returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_id = 1

    db_note = Note(
        note_id=note_id,
        note_title="Note 1",
        note_text="Text 1",
        author_id=1,
        is_public=True,
    )
    mock_db.execute.return_value.scalar_one_or_none.return_value = db_note

    note = get_note_by_id(note_id)

    assert note == db_note
    mock_db.execute.assert_called_once()
    args, _ = mock_db.execute.call_args
    query: Select[Tuple[Note]] = args[0]
    assert query._whereclause.compare(Note.note_id == note_id)


@patch("src.db.notes.get_db")
def test_create_note(mock_get_db):
    """
    GIVEN a note title, text, author ID, and public status
    WHEN create_note is called
    THEN the note is created and returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    note_title = "Note 1"
    note_text = "Text 1"
    author_id = 1
    is_public = True

    db_note = Note(
        note_title=note_title,
        note_text=note_text,
        author_id=author_id,
        is_public=is_public,
    )

    note = create_note(note_title, note_text, author_id, is_public)

    assert note == db_note
    args, _ = mock_db.add.call_args
    query = args[0]
    assert query == db_note
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(db_note)
