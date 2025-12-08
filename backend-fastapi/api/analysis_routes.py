from fastapi import APIRouter, Query, HTTPException, status
import db_utils
from models.analysis import *
from models.common import *

router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis"]
)


@router.get("", response_model=PaginatedResponse[Analysis])
def list_analysis(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        10, ge=1, le=100, description="Number of items per page")
):
    # TODO
    data, total = db_utils.list_analyses(page=page, per_page=per_page)

    return {
        "pagination": {"page": page, "per_page": per_page, "total": total},
        "elements": data
    }


@router.get("/{analysis_id}", response_model=Analysis)
def get_analysis_detail(analysis_id: int):
    # TODO
    analysis = db_utils.get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
def create_analysis(analysis_create: AnalysisCreate):
    # TODO
    analysis_id = db_utils.create_analysis(
        name=analysis_create.name,
        origin_id=analysis_create.origin_id,
        classes=analysis_create.classes
    )
    if analysis_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create analysis")
    analysis = db_utils.get_analysis(analysis_id)
    return analysis


@router.patch("/{analysis_id}", response_model=Analysis)
def update_analysis(analysis_id: int, analysis_update: AnalysisUpdate):
    # TODO
    success = db_utils.update_analysis(
        analysis_id=analysis_id,
        name=analysis_update.name,
        origin_id=analysis_update.origin_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update analysis")
    analysis = db_utils.get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int):
    # TODO
    success = db_utils.delete_analysis(analysis_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete analysis")
    return None