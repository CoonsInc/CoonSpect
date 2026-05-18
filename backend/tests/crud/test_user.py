from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import UserCRUD
from src.infra.db.models.user import User


@pytest.fixture
async def user_crud(db_session: AsyncSession) -> UserCRUD:
    return UserCRUD(db_session)


@pytest.mark.asyncio
async def test_create_user_success(user_crud: UserCRUD) -> None:
    user_data = {"username": "new_user", "password_hash": "hashed_string_123"}
    db_user = await user_crud.create(obj_in=user_data)

    assert db_user.id is not None
    assert db_user.username == "new_user"
    assert db_user.password_hash == "hashed_string_123"


@pytest.mark.asyncio
async def test_read_by_username_exists(
    user_crud: UserCRUD, db_session: AsyncSession
) -> None:
    username = "unique_bob"
    new_user = User(id=uuid4(), username=username, password_hash="secret")
    db_session.add(new_user)
    await db_session.commit()

    found_user = await user_crud.read_by_username(username=username)

    assert found_user is not None
    assert found_user.id == new_user.id
    assert found_user.username == username


@pytest.mark.asyncio
async def test_read_by_username_not_found(user_crud: UserCRUD) -> None:
    found_user = await user_crud.read_by_username(username="ghost")
    assert found_user is None


@pytest.mark.asyncio
async def test_read_user_by_id(user_crud: UserCRUD, db_session: AsyncSession) -> None:
    user_id = uuid4()
    new_user = User(id=user_id, username="alice", password_hash="hash")
    db_session.add(new_user)
    await db_session.commit()

    db_user = await user_crud.read(id=user_id)
    assert db_user is not None
    assert db_user.username == "alice"


@pytest.mark.asyncio
async def test_update_user_password(
    user_crud: UserCRUD, db_session: AsyncSession
) -> None:
    user = User(id=uuid4(), username="bob", password_hash="old_hash")
    db_session.add(user)
    await db_session.commit()

    new_data = {"password_hash": "new_awesome_hash"}
    updated_user = await user_crud.update(db_obj=user, update_data=new_data)

    assert updated_user.password_hash == "new_awesome_hash"
    assert updated_user.username == "bob"


@pytest.mark.asyncio
async def test_update_user_identity(
    user_crud: UserCRUD, db_session: AsyncSession
) -> None:
    user = User(id=uuid4(), username="original_name", password_hash="hash")
    db_session.add(user)
    await db_session.commit()

    updated_user = await user_crud.update(
        db_obj=user, update_data={"username": "new_name"}
    )

    assert updated_user.username == "new_name"

    refreshed_user = await user_crud.read_by_username("new_name")
    assert refreshed_user is not None
    assert refreshed_user.id == user.id


@pytest.mark.asyncio
async def test_delete_user_success(
    user_crud: UserCRUD, db_session: AsyncSession
) -> None:
    user = User(id=uuid4(), username="to_be_deleted", password_hash="...")
    db_session.add(user)
    await db_session.commit()

    result = await user_crud.delete(db_obj=user)
    assert result is True

    db_user = await user_crud.read(id=user.id)
    assert db_user is None
