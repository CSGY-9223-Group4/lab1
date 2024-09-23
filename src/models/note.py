from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER
from src.db.database import Base

class Note(Base):
    """
    Represents a note in the application.
    """
    __tablename__ = 'notes'

    note_id = Column(INTEGER(display_width=11), primary_key=True, autoincrement=True)
    note_title = Column(String(255), nullable=False)
    note_text = Column(Text, nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    author_id = Column(INTEGER(display_width=11), ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship to the User model
    author_user = relationship("User", back_populates="notes")

    def __repr__(self):
        return (
            f"<Note(note_id={self.note_id}, title='{self.note_title}', "
            f"public={self.is_public}, author_id={self.author_id}, created_at={self.created_at})>"
        )

    def to_dict(self):
        return {
            "note_id": self.note_id,
            "title": self.note_title,
            "text": self.note_text,
            "public": self.is_public,
            "author": self.author_user.username,
            "created_at": self.created_at.isoformat()  # Convert datetime to string
        }
