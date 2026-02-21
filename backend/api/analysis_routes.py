import json
import logging
import sqlite3
from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.db import db_utils
from backend.models.schemas.analysis import (
    AnalysisCreate,
    AnalysisFilters,
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
    name: Annotated[List[str] | None, Query(description="Filter by name (partial match)")] = None,
    owner: Annotated[List[str] | None, Query(description="Filter by owner ID")] = None,
    analysis_status: Annotated[
        List[AnalysisStatus] | None, Query(alias="status", description="Filter by status")
    ] = None,
    date_from: Annotated[datetime | None, Query(description="Created after (ISO format)")] = None,
    date_to: Annotated[datetime | None, Query(description="Created before (ISO format)")] = None,
) -> PaginatedResponse[AnalysisSummaryPublic]:
    """
    Retrieve a paginated and filtered list of all analyses.

    Args:
        page: The page number to retrieve.
        per_page: The number of elements per page.
        sort_column: The database column to sort by.
        sort_direction: The direction (ASC/DESC) for sorting.
        name: List of partial names to filter by.
        owner: List of repository owner logins to filter by.
        analysis_status: List of statuses to filter by.
        date_from: Start date filter.
        date_to: End date filter.

    Returns:
        PaginatedResponse: Containing the requested elements and metadata.

    Raises:
        HTTPException: 503 if the database is offline, 500 for other internal errors.
    """
    try:
        filters = AnalysisFilters(
            name=name,
            owner=owner,
            status=analysis_status,
            date_from=date_from,
            date_to=date_to,
        )

        data, total = db_utils.get_analyses(
            page=page, per_page=per_page, sorting=Sorting(column=sort_column, direction=sort_direction), filters=filters
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
    """
    Retrieve the full details of a specific analysis by ID.

    Args:
        analysis_id: The unique ID of the analysis.

    Returns:
        AnalysisPublic: The complete analysis data.

    Raises:
        HTTPException: 404 if not found, 503 if DB error, 500 otherwise.
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


@router.post("", response_model=AnalysisPublic, status_code=status.HTTP_201_CREATED, operation_id="create_analysis")
def create_analysis(analysis_create: AnalysisCreate, background_tasks: BackgroundTasks) -> AnalysisPublic | None:
    """
    Trigger a new repository analysis.

    Creates an 'IN_PROGRESS' record in the database and queues the actual
    cloning and analysis as a FastAPI BackgroundTask.

    Args:
        analysis_create: Object containing the repo_url to analyze.
        background_tasks: FastAPI helper to run logic after the response is sent.

    Returns:
        AnalysisPublic: The newly created placeholder analysis.
    """
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
    """
    Delete an analysis record (soft-delete).

    Args:
        analysis_id: The unique ID to delete.

    Raises:
        HTTPException: 404 if ID doesn't exist.
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


@router.post(
    "/upload", response_model=AnalysisPublic, status_code=status.HTTP_201_CREATED, operation_id="upload_analysis"
)
async def upload_analysis(file: Annotated[UploadFile, File()]) -> AnalysisPublic:
    """
    Import a previously exported analysis from a JSON file.

    Validates the JSON against the AnalysisPublic schema and generates
    new primary keys in the database to prevent collisions.

    Args:
        file: The JSON file to upload.

    Returns:
        AnalysisPublic: The newly created analysis record.
    """
    if file.content_type != "application/json" and file.filename and not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only JSON files are allowed."
        )

    try:
        content = await file.read()
        json_data = json.loads(content)

        analysis_model = AnalysisPublic(**json_data)
        imported_analysis = db_utils.upload_analysis_data(analysis_model)

        if not imported_analysis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading the analysis"
            )

        return imported_analysis

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format.") from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Schema validation failed: {e.errors()}"
        ) from e
    except Exception as e:
        logger.error(f"Error uploading analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during upload processing"
        ) from e


@router.get("/{analysis_id}/download", operation_id="download_analysis")
def download_analysis(analysis_id: int) -> JSONResponse:
    """
    Export an analysis's full data as a downloadable JSON file.

    Args:
        analysis_id: The ID of the analysis to export.

    Returns:
        JSONResponse: File attachment response with JSON content.
    """
    try:
        analysis = db_utils.get_analysis_details(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Analysis with ID {analysis_id} not found"
            )

        # Use model_dump(mode='json') to automatically serialize datetime fields to ISO strings
        analysis_dict = analysis.model_dump(mode="json")
        filename = f"analysis_{analysis.name}_{analysis.id}.json"

        return JSONResponse(
            content=analysis_dict,
            headers={"Content-Disposition": f"attachment; filename={filename}", "Content-Type": "application/json"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading analysis {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating download file"
        ) from e


def run_full_analysis_process(analysis_id: int, repo_url: str) -> None:
    """
    Execute the core analysis logic outside the request/response cycle.

    This helper handles cloning the repository, running the AST analyzer,
    fetching GitHub metadata, and updating the database with the results.

    Args:
        analysis_id: The database ID of the analysis record.
        repo_url: The URL of the repository to clone and analyze.
    """
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
