from typing import Any, Protocol, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession


class HasID(Protocol):
    id: ColumnElement[UUID]


ModelType = TypeVar("ModelType", bound=HasID)


class BaseCRUD[ModelType: HasID]:
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def read(self, id: UUID) -> ModelType | None:
        """Получение одной записи по UUID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create(self, obj_in: ModelType | dict[str, Any] | BaseModel) -> ModelType:
        """
        Создание записи. Принимает объект модели, словарь или Pydantic-схему.
        """
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        elif isinstance(obj_in, BaseModel):
            db_obj = self.model(**obj_in.model_dump())
        else:
            db_obj = obj_in

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ModelType, update_data: ModelType | dict[str, Any] | BaseModel
    ) -> ModelType:
        """
        Обновление записи.
        """
        if isinstance(update_data, dict):
            update_dict = update_data
        elif isinstance(update_data, BaseModel):
            update_dict = update_data.model_dump(exclude_unset=True)
        else:
            # Вытаскиваем данные из переданного объекта модели
            update_dict = {
                k: v for k, v in update_data.__dict__.items() if not k.startswith("_")
            }

        for field, value in update_dict.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> bool:
        """Удаление записи из БД."""
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
