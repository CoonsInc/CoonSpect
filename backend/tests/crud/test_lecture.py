from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.sorting import LectureSortBy, SortOrder
from src.crud.lecture import LectureCRUD
from src.infra.db.models.lecture import Lecture
from src.infra.db.models.user import User


@pytest.fixture
async def lecture_crud(db_session: AsyncSession) -> LectureCRUD:
    return LectureCRUD(db_session)


@pytest.mark.asyncio
async def test_get_list_pagination_logic(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    lectures: list[Lecture] = [
        Lecture(
            id=uuid4(),
            name=f"Lec {i}",
            user_id=sample_user.id,
            text=f"Content {i}",
            audio_url="bucket/audio",
            public=True,
        )
        for i in range(5)
    ]
    db_session.add_all(lectures)
    await db_session.commit()

    items, total, pages = await lecture_crud.get_list(
        page=1, limit=2, sort_by=LectureSortBy.CREATED_AT, order=SortOrder.DESC
    )
    assert total == 5
    assert pages == 3
    assert len(items) == 2

    items, total, pages = await lecture_crud.get_list(
        page=3, limit=2, sort_by=LectureSortBy.CREATED_AT, order=SortOrder.DESC
    )
    assert len(items) == 1

    items, total, pages = await lecture_crud.get_list(
        page=99, limit=2, sort_by=LectureSortBy.CREATED_AT, order=SortOrder.DESC
    )
    assert items == []


@pytest.mark.asyncio
async def test_get_list_sorting(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    l1 = Lecture(
        id=uuid4(),
        name="AAA",
        user_id=sample_user.id,
        text="some text",
        audio_url="lectures/test.mp3",
        public=True,
    )
    l2 = Lecture(
        id=uuid4(),
        name="ZZZ",
        user_id=sample_user.id,
        text="other text",
        audio_url="lectures/test.mp3",
        public=True,
    )
    db_session.add_all([l1, l2])
    await db_session.commit()

    items, _, _ = await lecture_crud.get_list(
        page=1, limit=20, sort_by=LectureSortBy.NAME, order=SortOrder.ASC
    )
    assert items[0].name == "AAA"

    items, _, _ = await lecture_crud.get_list(
        page=1, limit=20, sort_by=LectureSortBy.NAME, order=SortOrder.DESC
    )
    assert items[0].name == "ZZZ"


@pytest.mark.asyncio
async def test_get_list_filter_by_user(
    lecture_crud: LectureCRUD, db_session: AsyncSession
) -> None:
    u1_id: UUID = uuid4()
    u2_id: UUID = uuid4()

    db_session.add_all(
        [
            User(id=u1_id, username="u1", password_hash="."),
            User(id=u2_id, username="u2", password_hash="."),
        ]
    )

    db_session.add_all(
        [
            Lecture(
                id=uuid4(),
                name="U1 Lec",
                user_id=u1_id,
                text="t1",
                audio_url="lectures/test.mp3",
                public=True,
            ),
            Lecture(
                id=uuid4(),
                name="U2 Lec",
                user_id=u1_id,
                text="t1",
                audio_url="lectures/test.mp3",
            ),
        ]
    )
    await db_session.commit()

    items, total, _ = await lecture_crud.get_list(
        page=1,
        limit=20,
        user_id=u2_id,
        sort_by=LectureSortBy.CREATED_AT,
        order=SortOrder.DESC,
    )
    assert total == 1
    assert items[0].name == "U1 Lec"


@pytest.mark.asyncio
async def test_get_list_joinedload_user(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    lec = Lecture(
        id=uuid4(),
        name="Joined Lec",
        user_id=sample_user.id,
        text="joined text",
        audio_url="lectures/test.mp3",
        public=True,
    )
    db_session.add(lec)
    await db_session.commit()

    items, _, _ = await lecture_crud.get_list(
        page=1, limit=1, sort_by=LectureSortBy.CREATED_AT, order=SortOrder.DESC
    )
    assert items[0].user.username == sample_user.username


@pytest.mark.asyncio
async def test_create_lecture(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    lecture_data = {
        "name": "New Architecture",
        "text": "History of Roman architecture",
        "lecturer": "Dr. Smith",
        "user_id": sample_user.id,
    }

    db_obj = await lecture_crud.create(obj_in=lecture_data)

    assert db_obj.id is not None
    assert db_obj.name == "New Architecture"
    assert db_obj.user_id == sample_user.id


@pytest.mark.asyncio
async def test_read_lecture(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    lec = Lecture(
        id=uuid4(),
        name="Read Me",
        text="Some text",
        user_id=sample_user.id,
        audio_url="lectures/test.mp3",
    )
    db_session.add(lec)
    await db_session.commit()

    found_obj = await lecture_crud.read(id=lec.id)

    assert found_obj is not None
    assert found_obj.name == "Read Me"

    not_found = await lecture_crud.read(id=uuid4())
    assert not_found is None


@pytest.mark.asyncio
async def test_update_lecture_fields(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    lec = Lecture(
        id=uuid4(),
        name="Old Name",
        text="Old Text",
        user_id=sample_user.id,
        audio_url="lectures/test.mp3",
    )
    db_session.add(lec)
    await db_session.commit()

    update_data = {"name": "Updated Name"}
    updated_obj = await lecture_crud.update(db_obj=lec, update_data=update_data)

    assert updated_obj.name == "Updated Name"
    assert updated_obj.text == "Old Text"


@pytest.mark.asyncio
async def test_delete_lecture(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    lec = Lecture(
        id=uuid4(),
        name="To Delete",
        text="...",
        user_id=sample_user.id,
        audio_url="lectures/test.mp3",
    )
    db_session.add(lec)
    await db_session.commit()

    result = await lecture_crud.delete(db_obj=lec)
    assert result is True

    found = await lecture_crud.read(id=lec.id)
    assert found is None


@pytest.mark.asyncio
async def test_get_list_search_by_name(
    lecture_crud: LectureCRUD, sample_user: User, db_session: AsyncSession
) -> None:
    db_session.add_all(
        [
            Lecture(
                id=uuid4(),
                name="Python Advanced",
                user_id=sample_user.id,
                text="text",
                audio_url="url",
                public=True,
            ),
            Lecture(
                id=uuid4(),
                name="Python Basics",
                user_id=sample_user.id,
                text="text",
                audio_url="url",
                public=True,
            ),
            Lecture(
                id=uuid4(),
                name="Java Intro",
                user_id=sample_user.id,
                text="text",
                audio_url="url",
                public=True,
            ),
        ]
    )
    await db_session.commit()

    items, total, _ = await lecture_crud.get_list(
        page=1,
        limit=10,
        sort_by=LectureSortBy.NAME,
        order=SortOrder.ASC,
        search_name="python",
    )

    assert total == 2
    assert len(items) == 2

    for item in items:
        assert "Python" in item.name

    items_empty, total_empty, _ = await lecture_crud.get_list(
        page=1,
        limit=10,
        sort_by=LectureSortBy.NAME,
        order=SortOrder.ASC,
        search_name="Golang",
    )
    assert total_empty == 0
    assert len(items_empty) == 0
