import logging
from datetime import date
#from sqlalchemy.exc import IntegrityError
#from app.core.exceptions.http_exceptions import bad_request, not_found, conflict
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.schemas.statistics_schema import DashboardStatistics

logger = logging.getLogger(__name__)

class StatisticsService:
    def __init__(self,
                 transaction_repository: TransactionRepository,
                 carpooling_repository: CarpoolingRepository,
                 ) -> None:
        self.transaction_repository = transaction_repository
        self.carpooling_repository = carpooling_repository

    async def get_dashboard_statistics(self) -> DashboardStatistics:
        revenues = await (self.transaction_repository.get_revenues_last_7_days())
        carpoolings = await (self.carpooling_repository.get_carpooling_last_7_days())

        week_revenue = sum(
            revenue.amount
            for revenue in revenues
        )
        week_carpooling = sum(
            carpooling.count
            for carpooling in carpoolings)

        today = date.today()

        today_revenue = next(
            (
                revenue.amount
                for revenue in revenues
                if revenue.date == today
            ),
            0,
        )

        today_carpooling = next(
            (
                carpooling.count
                for carpooling in carpoolings
                if carpooling.date == today
            ),
            0,
        )

        return DashboardStatistics(
            today_revenue=today_revenue,
            week_revenue=week_revenue,
            today_carpooling=today_carpooling,
            week_carpooling=week_carpooling,
            revenues=revenues,
            carpoolings=carpoolings,
        )