from src.models.user import User


def test_create_user(session):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, password, and created_at fields are defined correctly

    :param session: Pytest fixture for SQLAlchemy session
    :return:
    """
    user = User(username="testuser", password="password123")
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.password == "password123"
    assert retrieved_user.created_at is not None


def test_user_repr(session):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the __repr__ output is as expected

    :param session: Pytest fixture for SQLAlchemy session
    :return:
    """
    user = User(username="testuser2", password="password456")
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(username="testuser2").first()
    assert (
        repr(retrieved_user)
        == f"<User(user_id={retrieved_user.user_id}, "
        + f"username='{retrieved_user.username}', created_at='{retrieved_user.created_at}')>"
    )
