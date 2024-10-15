from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER

from ..db.database import Base


class User(Base):
    """
    Represents a user in the application.
    """

    __tablename__ = "users"

    user_id = Column(INTEGER(display_width=11), primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    # Add other user-related fields as needed

    # Relationship to the Note model
    notes = relationship(
        "Note", back_populates="author_user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', created_at='{self.created_at}')>"
