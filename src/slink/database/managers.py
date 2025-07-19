from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

import logging
from typing import Optional, Sequence

from auth.utils import hash_password
from auth.validation import validate_email

from .models import User, Link
from exceptions import bad_email_exc, server_exc
from config import configure_logging


configure_logging()
log = logging.getLogger(__name__)


class PSQLManager:
    async def register(self, username: str, email: str, password: str, session: AsyncSession) -> Optional[bool]:
        try:
            result_user = await session.execute(select(User).where(User.username == username, User.email == email))
            user = result_user.scalar_one_or_none()

            if user:
                return False
            
            hashed_password = hash_password(password).decode('utf-8')
            validate_email(email)

            new_user = User(username=username, email=email, password=hashed_password)

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return True

        except IntegrityError:
            return None
        
        except HTTPException:
            raise bad_email_exc
        
        except Exception as e:
            log.error(e)
            raise server_exc
        

    async def get_all_links(self, current_user: User, session: AsyncSession) -> Sequence[Link]:
        try:
            result_links = await session.execute(
                select(Link).where(Link.user_id == current_user.id).order_by(Link.created_at.desc())
            )
            links = result_links.scalars().all()
            
            return links

        except Exception as e:
            log.error(e)
            raise server_exc
        

    async def add_link(self, long_link: str, short_link: str, current_user: User, session: AsyncSession) -> None:
        try:
            new_link = Link(long_link=long_link, short_link=short_link, user_id=current_user.id)

            session.add(new_link)
            await session.commit()
            await session.refresh(new_link)

        except Exception as e:
            log.error(e)
            raise server_exc


    async def delete_link(self, short_link: str, current_user: User, session: AsyncSession) -> None:
        try:
            result_link = await session.execute(
                select(Link).where(Link.user_id == current_user.id, Link.short_link == short_link)
            )
            link = result_link.scalar_one_or_none()

            await session.delete(link)
            await session.commit()

        except Exception as e:
            log.error(e)
            raise server_exc
        

psql_manager = PSQLManager()