from collections.abc import Sequence
from ..db import notes as NotesDB
from ..models.note import Note


class NoteService:
    def __init__(self, notes_db: NotesDB):
        self.notes_db = notes_db

    def get_notes(
        self, author_id: int, page: int = 1, page_size: int = 10
    ) -> Sequence[Note]:
        return self.notes_db.get_notes_for_user(author_id, page, page_size)

    def get_note_by_id(self, author_id: int, note_id: int) -> Note | None:
        note = self.notes_db.get_note_by_id(note_id)
        if note is None:
            return None

        return note if note.is_public or note.author_id == author_id else None

    def create_note(
        self, note_title: str, note_text: str, author_id: int, is_public: bool = False
    ) -> Note:
        return self.notes_db.create_note(note_title, note_text, author_id, is_public)

    def update_note(
        self,
        note_id: int,
        note_title: str,
        note_text: str,
        author_id: int,
        is_public: bool = False,
    ) -> Note:
        return self.notes_db.update_note(
            note_id, note_title, note_text, author_id, is_public
        )

    def delete_note(self, author_id: int, note_id: int) -> bool:
        return self.notes_db.delete_note(author_id, note_id)


note_service = NoteService(NotesDB)
