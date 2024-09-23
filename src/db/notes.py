from ..models.user import User
from ..models.note import Note
from .database import SessionLocal
from sqlalchemy import or_


# Create a new session
db = SessionLocal()

def get_notes_for_user(user_id: int) -> list[Note]:
    return db.query(Note).filter(
        or_(
            Note.is_public == True,
            Note.author_id == User.user_id
        )
    ).all()

def create_note(note_title: str, note_text: str, author_id: int, is_public: bool = False) -> Note:
    db_note = Note(
        note_title=note_title,
        note_text=note_text,
        is_public=is_public,
        author_id=author_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note
