from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.domain.entities import SavedUserEntity, UserEntity
from src.modules.users.infrastructure.mappers import user_entity_to_model, user_model_to_entity


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_user(self, user: UserEntity) -> SavedUserEntity:
        model = user_entity_to_model(user_entity=user)

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return user_model_to_entity(user_model=model)
