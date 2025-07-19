from fastapi import APIRouter, Request, Depends, Form

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
from database.models import User, Link
from database.managers import psql_manager

from auth import get_current_auth_user
from config import configure_logging, TOKEN

import httpx


configure_logging()
log = logging.getLogger(__name__)


router = APIRouter(tags=['Link'])


headers = {"Authorization": f"Bearer {TOKEN}"}


@router.post("/create_short_link")
async def create_short_link(long_link: str = Form(...)) -> Any:
    data = {
        "url": long_link,
        "domain": "tiny.one",
        "description": "null"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.tinyurl.com/create", headers=headers, data=data)

        ans = response.json()
        log.debug(None, ans)

        short_link = ans["data"]["tiny_url"]

    return short_link


@router.post("/auth_create_short_link")
async def auth_create_short_link(
    long_link: str = Form(...),
    current_user: User = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    
    data = {
        "url": long_link,
        "domain": "tiny.one",
        "description": current_user.username
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.tinyurl.com/create", headers=headers, data=data)

        ans = response.json()
        log.debug(current_user.username, ans)

        short_link = ans["data"]["tiny_url"]

    await psql_manager.add_link(long_link, short_link, current_user, session)

    return short_link


@router.delete("/delete_short_link")
async def delete_short_link(
    short_link: str,
    current_user: User = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    
    await psql_manager.delete_link(short_link, current_user, session)