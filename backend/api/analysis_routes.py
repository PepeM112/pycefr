import logging
import sqlite3
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from backend.db import db_utils
from backend.models.schemas.analysis import (
    AnalysisCreate,
    AnalysisPublic,
    AnalysisSortColumn,
    AnalysisStatus,
    AnalysisSummaryPublic,
)
from backend.models.schemas.common import PaginatedResponse, Pagination, SortDirection, Sorting
from backend.services.analyzer.analyzer import Analyzer
from backend.services.analyzer.github_manager import GitHubManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyses", tags=["Analysis"])


@router.get("", response_model=PaginatedResponse[AnalysisSummaryPublic], operation_id="list_analysis")
def list_analysis(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, description="Number of items per page"),
    sort_column: Annotated[AnalysisSortColumn, Query(description="Column to sort by")] = AnalysisSortColumn.ID,
    sort_direction: Annotated[SortDirection, Query(description="Sort direction (ASC or DESC)")] = SortDirection.DESC,
) -> PaginatedResponse[AnalysisSummaryPublic]:
    try:
        data, total = db_utils.get_analyses(
            page=page, per_page=per_page, sorting=Sorting(column=sort_column, direction=sort_direction)
        )

        return PaginatedResponse[AnalysisSummaryPublic](
            pagination=Pagination(page=page, per_page=per_page, total=total),
            elements=data,
        )
    except (sqlite3.OperationalError, ConnectionError) as e:
        logger.critical(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is currently unavailable.",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in list_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving the analysis list"
        ) from e


@router.get("/{analysis_id}", response_model=AnalysisPublic, operation_id="get_analysis_detail")
def get_analysis_detail(analysis_id: int) -> AnalysisPublic | None:
    try:
        analysis = db_utils.get_analysis_details(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis with ID {analysis_id} not found"
            )
        return analysis
    except HTTPException:
        raise
    except (sqlite3.OperationalError, ConnectionError) as e:
        logger.critical(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is currently unavailable.",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in get_analysis_detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving the analysis details"
        ) from e


@router.post("", response_model=AnalysisPublic, status_code=status.HTTP_201_CREATED, operation_id="create_analysis")
def create_analysis(analysis_create: AnalysisCreate, background_tasks: BackgroundTasks) -> AnalysisPublic | None:
    analysis: AnalysisPublic | None = None

    try:
        analysis = db_utils.create_empty_analysis(analysis_create.repo_url)

        if analysis is None:
            logger.error(f"Failed to create database entry for: {analysis_create.repo_url}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating the analysis")

        background_tasks.add_task(run_full_analysis_process, analysis.id, analysis_create.repo_url)

        return analysis

    except Exception as e:
        if analysis and analysis.id:
            logger.warning(f"Marking analysis {analysis.id} as failed due to request error")
            db_utils.mark_analysis_as_failed(analysis.id, f"Initialization error: {str(e)}")

        if isinstance(e, HTTPException):
            raise e

        if isinstance(e, (sqlite3.OperationalError, ConnectionError)):
            logger.critical(f"Database connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is currently unavailable.",
            ) from e

        logger.error(f"Unexpected error in create_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating the analysis"
        ) from e


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="delete_analysis")
def delete_analysis(analysis_id: int) -> None:
    try:
        success = db_utils.delete_analysis(analysis_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis {analysis_id} not found")
        return None
    except HTTPException:
        raise
    except (sqlite3.OperationalError, ConnectionError) as e:
        logger.critical(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is currently unavailable.",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in delete_analysis ID {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting the analysis"
        ) from e


def run_full_analysis_process(analysis_id: int, repo_url: str) -> None:
    """This function runs outside the HTTP request cycle."""
    try:
        gh = GitHubManager(repo_url=repo_url, is_cli=False)
        gh.validate_repo_url()
        cloned_repo = gh.clone_repo()

        an = Analyzer(cloned_repo, is_cli=False)
        an.analyse_project()

        repo_info = gh.get_repo_info()

        analysis_result = an.get_results()

        analysis_result.repo = repo_info
        analysis_result.status = AnalysisStatus.COMPLETED

        db_utils.update_analysis_results(analysis_id, analysis_result)

    except (ValueError, FileNotFoundError, PermissionError) as e:
        logger.error(f"Analysis {analysis_id} validation failed: {e}")
        db_utils.mark_analysis_as_failed(analysis_id, str(e))

    except Exception as e:
        logger.error(f"Analysis {analysis_id} crashed: {e}")
        db_utils.mark_analysis_as_failed(analysis_id, f"Internal Error: {e}")
    finally:
        Analyzer.delete_tmp_files()
