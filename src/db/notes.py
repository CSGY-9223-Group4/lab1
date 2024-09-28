from collections.abc import Sequence
from sqlalchemy import and_, delete, or_, select

from ..models.note import Note
from .database import get_db


def get_notes_for_user(author_id: int) -> Sequence[Note]:
    with get_db() as db:
        return (
            db.execute(
                select(Note).where(
                    or_(
                        Note.is_public == True,
                        Note.author_id == author_id,
                    )
                )
            )
            .scalars()
            .all()
        )


def get_note_by_id(note_id: int) -> Note | None:
    with get_db() as db:
        return db.execute(
            select(Note).where(Note.note_id == note_id)
        ).scalar_one_or_none()


def create_note(
    note_title: str, note_text: str, author_id: int, is_public: bool = False
) -> Note:
    db_note = Note(
        note_title=note_title,
        note_text=note_text,
        is_public=is_public,
        author_id=author_id,
    )
    with get_db() as db:
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note


def update_note(
    note_id: int,
    note_title: str,
    note_text: str,
    author_id: int,
    is_public: bool = False,
) -> Note | None:
    with get_db() as db:
        db_note = db.execute(
            select(Note).where(
                and_(
                    Note.author_id == author_id,
                    Note.note_id == note_id,
                )
            )
        ).scalar_one_or_none()

        if db_note is None:
            return None

        db_note.note_title = note_title
        db_note.note_text = note_text
        db_note.is_public = is_public
        db.commit()
        db.refresh(db_note)
        return db_note


def delete_note(author_id: int, note_id: int) -> bool:
    print(f"author_id: {author_id}, note_id: {note_id}")
    with get_db() as db:
        result = db.execute(
            delete(Note).where(
                and_(
                    Note.note_id == note_id,
                    Note.author_id == author_id,
                )
            )
        )
        db.commit()
        return result.rowcount > 0
