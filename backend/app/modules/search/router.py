from typing import Dict, List, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.search.service import GlobalSearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def global_search(
    q: str = Query("", min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GlobalSearchService(db)
    return await service.search_all(q)
