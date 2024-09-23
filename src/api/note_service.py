from ..models.note import Note
from ..db.notes import get_notes_for_user, create_note


def get_notes(user_id: int) -> list[Note]:
    return get_notes_for_user(user_id)

def post_note(note_title: str, note_text: str,  author_id: int, is_public: bool = False) -> Note:
    return create_note(note_title, note_text, author_id, is_public)