import logging
import sqlite3

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from backend.db import db_utils
from backend.models.schemas.analysis import (
    Analysis,
    AnalysisCreate,
    AnalysisStatus,
    AnalysisSummary,
)
from backend.models.schemas.common import PaginatedResponse, Pagination
from backend.services.analyzer.analyzer import Analyzer
from backend.services.analyzer.github_manager import GitHubManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyses", tags=["Analysis"])


@router.get("", response_model=PaginatedResponse[AnalysisSummary])
def list_analysis(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, description="Number of items per page"),
) -> PaginatedResponse[AnalysisSummary]:
    """
    Retrieves a paginated list of analysis summaries.

    Args:
        page (int): The current page number (starts at 1).
        per_page (int): The number of items to return per page.

    Returns:
        PaginatedResponse[AnalysisSummary]: A dictionary containing pagination metadata and the list of elements.

    Raises:
        HTTPException(503): If the database is unavailable.
        HTTPException(500): If an internal server error occurs.
    """
    try:
        data, total = db_utils.get_analyses(page=page, per_page=per_page)

        return PaginatedResponse[AnalysisSummary](
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


@router.get("/{analysis_id}", response_model=Analysis)
def get_analysis_detail(analysis_id: int) -> Analysis | None:
    """
    Fetches the full details of a specific analysis.

    Args:
        analysis_id (int): The unique identifier of the analysis.

    Returns:
        AnalysisResult | FullAnalysisResult: The complete analysis object with hydrated class levels.

    Raises:
        HTTPException(404): If the analysis does not exist.
        HTTPException(503): If the database is unavailable.
        HTTPException(500): If an internal server error occurs.
    """
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


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
def create_analysis(analysis_create: AnalysisCreate, background_tasks: BackgroundTasks) -> Analysis | None:
    """
    Creates a new analysis record.

    Raises:
        HTTPException(422): If there are duplicate classes.
        HTTPException(503): If the database is unavailable.
        HTTPException(500): If the creation fails.
    """
    try:
        analysis_id = db_utils.create_empty_analysis(analysis_create.repo_url)
        if analysis_id is None:
            logger.error(f"Failed to create database entry for: {analysis_create.repo_url}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating the analysis")

        background_tasks.add_task(run_full_analysis_process, analysis_id, analysis_create.repo_url)
        analysis_result = db_utils.get_analysis_details(analysis_id)
        if analysis_result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis created but could not be retrieved."
            )

        return analysis_result
    except HTTPException:
        raise
    except (sqlite3.OperationalError, ConnectionError) as e:
        logger.critical(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is currently unavailable.",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in create_analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating the analysis"
        ) from e


def delete_analysis(analysis_id: int) -> None:
    """
    Deletes an analysis and all associated classes.

    Args:
        analysis_id (int): The ID of the analysis to delete.

    Raises:
        HTTPException(404): If the analysis does not exist.
        HTTPException(503): If the database is unavailable.
        HTTPException(500): If the deletion fails.
    """
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


async def run_full_analysis_process(analysis_id: int, repo_url: str) -> None:
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
