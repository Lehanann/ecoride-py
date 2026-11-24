from datetime import date as Date
from pydantic import BaseModel, Field, ConfigDict

class RevenueStat(BaseModel):
    """
    Schema used to represent revenue statistics per day and on the 7 last days.

    Attributes:
        date (date): Revenue per day.
        amount (float): Revenue on the last 7 days.
    """
    date: Date = Field(..., description="Revenue date.")
    amount: float = Field(..., description="Revenue amount for the day.")

    model_config = ConfigDict()

class CarpoolingStat(BaseModel):
    """
    Schema used to represent carpooling statistics per day and on the 7 last days.

    Attributes:
        date (date): Carpooling per day.
        count (int): Carpooling on the last 7 days.
    """
    date: Date = Field(..., description="Carpool date.")
    count: int = Field(..., description="Number of carpools.")

    model_config = ConfigDict()

class DashboardStatistics(BaseModel):
    """
    Schema used to represent dashboard statistics with list of revenues and carpools.

    Attributes:

    """

    today_revenue: float = Field(..., description="Total revenue today.")
    week_revenue: float = Field(..., description="Total revenue over the last 7 days.")
    today_carpooling: int = Field(..., description="Total carpool today.")
    week_carpooling: int = Field(..., description="Total carpool over the last 7 days.")
    revenues: list[RevenueStat] = Field(..., description="List of revenues.")
    carpoolings: list[CarpoolingStat] = Field(..., description="List of carpools.")

    model_config = ConfigDict()
