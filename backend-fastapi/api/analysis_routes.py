from fastapi import APIRouter, Query, HTTPException, status
import db_utils
from models.analysis import *
from models.common import *

router = APIRouter(
    prefix="/api/analyses",
    tags=["Analysis"]
)


@router.get("", response_model=PaginatedResponse[AnalysisList])
def list_analysis(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        10, ge=1, le=100, description="Number of items per page")
):

    try:
        data, total = db_utils.get_analyses(page=page, per_page=per_page)

        return {
            "pagination": {"page": page, "per_page": per_page, "total": total},
            "elements": data
        }
    except Exception as e:
        print(f"[ERROR] list_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving the analysis list"
        )


@router.get("/{analysis_id}", response_model=Analysis)
def get_analysis_detail(analysis_id: int):
    try:
        analysis = db_utils.get_analysis_details(analysis_id)
        if analysis is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID {analysis_id} not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_analysis_detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving the analysis details"
        )


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
def create_analysis(analysis_create: AnalysisCreate):
    try:
        analysis_id = db_utils.insert_full_analysis(
            name=analysis_create.name,
            origin=analysis_create.origin.value,
            classes=[c.model_dump() for c in analysis_create.classes]
        )
        if analysis_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create analysis"
            )

        return db_utils.get_analysis_details(analysis_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] create_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating the analysis"
        )


@router.patch("/{analysis_id}", response_model=Analysis)
def update_analysis(analysis_id: int, analysis_update: AnalysisUpdate):
    try:
        success = db_utils.update_analysis(
            analysis_id=analysis_id,
            name=analysis_update.name,
            origin=analysis_update.origin.value if analysis_update.origin else None,
            classes=[c.model_dump()
                     for c in analysis_update.classes] if analysis_update.classes else None
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID {analysis_id} not found"
            )

        return db_utils.get_analysis_details(analysis_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] update_analysis ID {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating the analysis"
        )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int):
    try:
        success = db_utils.delete_analysis(analysis_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found or already deleted"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] delete_analysis ID {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting the analysis"
        )
