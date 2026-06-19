from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.entities import SavedUserEntity, UserEntity
from src.modules.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_user(self, user: UserEntity) -> SavedUserEntity:
        model = User(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            telegram_id=user.telegram_id,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return SavedUserEntity(
            id=model.id,
            username=model.username,
            nickname=model.nickname,
            email=model.email,
            telegram_id=model.telegram_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
