from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

import db_utils
from models.analysis import Analysis, AnalysisCreate, AnalysisList, AnalysisUpdate
from models.common import PaginatedResponse, Pagination

router = APIRouter(prefix="/api/analyses", tags=["Analysis"])


@router.get("", response_model=PaginatedResponse[AnalysisList])
def list_analysis(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, description="Number of items per page"),
) -> PaginatedResponse[AnalysisList]:
    """
    Retrieves a paginated list of analysis summaries.

    Args:
        page (int): The current page number (starts at 1).
        per_page (int): The number of items to return per page.

    Returns:
        PaginatedResponse[AnalysisList]: A dictionary containing pagination metadata and the list of elements.

    Raises:
        HTTPException(500): If an internal database error occurs.
    """
    try:
        data, total = db_utils.get_analyses(page=page, per_page=per_page)

        return PaginatedResponse[AnalysisList](
            pagination=Pagination(page=page, per_page=per_page, total=total),
            elements=data,
        )
    except Exception as e:
        print(f"[ERROR] list_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving the analysis list"
        ) from e


@router.get("/{analysis_id}", response_model=Analysis)
def get_analysis_detail(analysis_id: int) -> Analysis:
    """
    Fetches the full details of a specific analysis, including nested classes.

    Args:
        analysis_id (int): The unique identifier of the analysis.

    Returns:
        Analysis: The complete analysis object with hydrated class levels.

    Raises:
        HTTPException(404): If the analysis does not exist.
        HTTPException(500): If an internal server error occurs.
    """
    try:
        analysis: Optional[Analysis] = db_utils.get_analysis_details(analysis_id)
        if analysis is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis with ID {analysis_id} not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_analysis_detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving the analysis details"
        ) from e


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
def create_analysis(analysis_create: AnalysisCreate) -> Optional[Analysis]:
    """
    Creates a new analysis record along with its nested code classes.

    Args:
        analysis_create (AnalysisCreate): The payload containing name, origin, and classes.

    Returns:
        Optional[Analysis]: The created analysis object with its generated ID.

    Raises:
        HTTPException(422): If there are duplicate classes in the request.
        HTTPException(500): If the creation fails due to server error.
    """
    try:
        analysis_id = db_utils.insert_full_analysis(analysis_create)
        if analysis_id is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create analysis")

        return db_utils.get_analysis_details(analysis_id)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Classes must be unique within an analysis. " + str(e),
        ) from e
    except Exception as e:
        print(f"[ERROR] create_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating the analysis"
        ) from e


@router.patch("/{analysis_id}", response_model=Analysis)
def update_analysis(analysis_id: int, analysis_update: AnalysisUpdate) -> Optional[Analysis]:
    """
    Updates an existing analysis.

    If 'classes' are provided, the existing classes are replaced entirely (Delete & Insert).
    If 'classes' is an empty list, all classes for this analysis are removed.

    Args:
        analysis_id (int): The ID of the analysis to update.
        analysis_update (AnalysisUpdate): The fields to update (name, origin, classes).

    Returns:
        Optional[Analysis]: The updated analysis object, or None if not found.

    Raises:
        HTTPException(404): If the analysis ID does not exist.
        HTTPException(422): If the new class list contains duplicates.
        HTTPException(500): If the update fails due to server error.
    """
    try:
        success = db_utils.update_analysis(analysis_id, analysis_update)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis with ID {analysis_id} not found"
            )

        return db_utils.get_analysis_details(analysis_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Classes must be unique within an analysis. " + str(e),
        ) from e
    except Exception as e:
        print(f"[ERROR] update_analysis ID {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating the analysis"
        ) from e


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int) -> None:
    """
    Deletes an analysis and all associated classes.

    Args:
        analysis_id (int): The ID of the analysis to delete.

    Raises:
        HTTPException(404): If the analysis does not exist.
        HTTPException(500): If the deletion fails.
    """
    try:
        success = db_utils.delete_analysis(analysis_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis {analysis_id} not found or already deleted"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] delete_analysis ID {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting the analysis"
        ) from e
