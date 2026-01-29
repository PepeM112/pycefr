import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from backend.db.label_utils import get_class_labels
from backend.models.schemas.class_model import ClassItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/labels", tags=["Labels"])


@router.get("/class", response_model=List[ClassItem], operation_id="class_label")
def class_label() -> List[ClassItem]:
    """
    Retrieves the complete list of code construct labels and their associated
    CEFR levels from the database.
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
