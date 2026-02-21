import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from backend.db.label_utils import get_class_labels
from backend.models.schemas.class_model import ClassPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/labels", tags=["Labels"])


@router.get("/class", response_model=List[ClassPublic], operation_id="class_label")
def class_label() -> List[ClassPublic]:
    """
    Retrieve all code construct labels and their assigned CEFR levels.

    This endpoint fetches the master list of classification identifiers
    (e.g., 'LIST_NESTED', 'CLASS_INHERITED') and their corresponding
    language levels (A1-C2) from the database.

    Returns:
        List[ClassPublic]: A list of objects containing ClassId and Level.

    Raises:
        HTTPException: 500 status code if there is an error accessing the
            labels in the database.
    """
    try:
        labels = get_class_labels()

        if not labels:
            logger.warning("No class labels found in the database")

        return labels
    except Exception as e:
        logger.error(f"Error retrieving class labels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving class labels",
        ) from e
