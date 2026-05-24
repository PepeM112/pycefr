import logging
import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.db import db_utils
from backend.models.schemas.stats import DashboardStats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("", response_model=DashboardStats, operation_id="get_dashboard_stats")
def get_dashboard_stats() -> DashboardStats:
    try:
        return db_utils.get_dashboard_stats()
    except (sqlite3.OperationalError, ConnectionError) as e:
        logger.critical(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is currently unavailable.",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in get_dashboard_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard stats",
        ) from e
