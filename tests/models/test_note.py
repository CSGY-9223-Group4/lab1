import pytest
import random
from string import ascii_letters
from src.models.user import User
from src.models.note import Note


@pytest.fixture(scope="function")
def note_author(session):
    user = User(
        username="".join([random.choice(ascii_letters) for _ in range(20)]),
        password="password123",
    )
    session.add(user)
    session.commit()
    return user


def test_create_note(session, note_author):
    """
    GIVEN a Note model
    WHEN a new Note is created
    THEN check the author_id, note_title, note_text, is_public, created_at, and updated_at fields are defined correctly

    :param session: Pytest fixture for SQLAlchemy session
    :return:
    """
    note = Note(
        author_id=note_author.user_id,
        note_title="Test Note",
        note_text="This is a test note",
        is_public=True,
    )
    session.add(note)
    session.commit()

    retrieved_note = session.query(Note).filter_by(note_title="Test Note").first()
    assert retrieved_note is not None
    assert retrieved_note.author_id == note_author.user_id
    assert retrieved_note.note_title == "Test Note"
    assert retrieved_note.note_text == "This is a test note"
    assert retrieved_note.is_public is True
    assert retrieved_note.created_at is not None
    assert retrieved_note.updated_at is not None


def test_note_repr(session, note_author):
    """
    GIVEN a Note model
    WHEN a new Note is created
    THEN check the __repr__ output is as expected

    :param session: Pytest fixture for SQLAlchemy session
    :return:
    """
    note = Note(
        author_id=note_author.user_id,
        note_title="Test Note",
        note_text="This is a test note",
        is_public=True,
    )
    session.add(note)
    session.commit()

    db_note = session.query(Note).filter_by(note_title="Test Note").first()
    assert repr(db_note) == (
        f"<Note(note_id={db_note.note_id}, title='{db_note.note_title}', "
        f"public={db_note.is_public}, author_id={db_note.author_id}, created_at={db_note.created_at}, "
        f"updated_at={db_note.updated_at})>"
    )


def test_delete_user_deletes_notes(session, note_author):
    """
    GIVEN a User and a Note model
    WHEN the User is deleted
    THEN check that the associated Note is also deleted

    :param session: Pytest fixture for SQLAlchemy session
    :param note_author: Fixture for creating a user
    :return:
    """
    # Create a note associated with the user
    note = Note(
        author_id=note_author.user_id,
        note_title="Note to be deleted",
        note_text="This note should be deleted",
        is_public=True,
    )
    session.add(note)
    session.commit()

    # Verify the note exists
    retrieved_note = (
        session.query(Note).filter_by(note_title="Note to be deleted").first()
    )
    assert retrieved_note is not None
    assert retrieved_note.author_user.user_id == note_author.user_id

    # Delete the user
    session.delete(note_author)
    session.commit()

    # Verify the note is deleted
    deleted_note = (
        session.query(Note).filter_by(note_title="Note to be deleted").first()
    )
    assert deleted_note is None
