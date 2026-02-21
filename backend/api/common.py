import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from backend.db.db_utils import get_unique_owners
from backend.models.schemas.common import EntityLabelString

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/common", tags=["Common"])


@router.get("/owners", response_model=List[EntityLabelString], operation_id="get_owners")
def get_owners(search: str | None = None, limit: int | None = None) -> List[EntityLabelString]:
    """
    Retrieve a unique list of repository owners found in the database.

    This endpoint is primarily used for populating filter dropdowns or search
    autocompletion in the frontend.

    Args:
        search (str | None): A search string to filter owners by name or login.
        limit (int | None): The maximum number of owner entities to return.

    Returns:
        List[EntityLabelString]: A list of objects containing owner IDs and labels.

    Raises:
        HTTPException: 500 status code if a database or server error occurs.
    """
    try:
        owners = get_unique_owners(search_query=search, limit=limit)

        if not owners:
            logger.warning("No owners found in the database")

        return owners
    except Exception as e:
        logger.error(f"Error retrieving owners: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving owners",
        ) from e
