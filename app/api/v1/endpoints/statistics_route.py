from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from databases.postgresql import get_session
from app.schemas.statistics_schema import DashboardStatistics
from app.services.statistics_service import StatisticsService
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.transaction_repository import TransactionRepository

router = APIRouter(prefix="/statistics", tags=["statistics"])

def get_statistics_service (db: AsyncSession = Depends(get_session)) -> StatisticsService:
    return StatisticsService(
        TransactionRepository(db),
        CarpoolingRepository(db)
    )

@router.get("/", response_model=DashboardStatistics)
async def get_dashboard_statistics(service: StatisticsService = Depends(get_statistics_service)):
    return await service.get_dashboard_statistics()