from backend.db.db_utils import get_analyses, get_analysis_details
from backend.models.schemas.analysis import AnalysisStatus
from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Origin


def test_get_analyses_comprehensive_summary() -> None:
    """Validate that the summary (list) returns aggregated data correctly."""
    analyses, total = get_analyses(page=1, per_page=10)

    assert total == 1
    summary = analyses[0]

    # Basic Data
    assert summary.name == "pycefr_testing"
    assert summary.origin == Origin.GITHUB
    assert summary.status == AnalysisStatus.COMPLETED
    assert summary.estimated_hours == 73.5

    # Aggregation Validation: In the seed, ClassId.7 appears in:
    # - File 1: 90 instances
    # - File 4: 1 instance
    # Expected total = 91
    class_7 = next(c for c in summary.classes if c.class_id == ClassId.DICT_SIMPLE)
    assert class_7.instances == 91
    assert class_7.level == 2


def test_get_analysis_details_deep_structure() -> None:
    """Validate the entire hierarchy of a detailed analysis."""
    analysis = get_analysis_details(1)

    assert analysis is not None

    # 1. Validate Files (Must be 4)
    assert len(analysis.file_classes) == 4
    filenames = [f.filename for f in analysis.file_classes]
    assert "backend/constants/analysis_rules.py" in filenames
    assert "backend/main.py" in filenames

    # 2. Validate classes of a specific file (File 1: analysis_rules.py)
    # According to the seed, it has 8 distinct classes
    file_1 = next(f for f in analysis.file_classes if f.filename == "backend/constants/analysis_rules.py")
    assert len(file_1.classes) == 8

    # Validate a specific class in file 1 (Class 65, Level 4, 1 instance)
    class_65 = next(c for c in file_1.classes if c.class_id == ClassId.CLASS_INHERITED)
    assert class_65.level == 4
    assert class_65.instances == 1

    # 3. Validate Repository Information
    repo = analysis.repo
    assert repo is not None
    assert repo.name == "pycefr"
    assert repo.owner.github_user == "PepeM112"
    assert repo.url == "https://github.com/PepeM112/pycefr"

    # 4. Validate commits (must be 3)
    assert len(repo.commits) == 3
    # Validate the commit of 'anapgh' (loc: 21355, hours: 37.77)
    commit_ana = next(c for c in repo.commits if c.username == "anapgh")
    assert commit_ana.loc == 21355
    assert commit_ana.estimated_hours == 37.77
    assert commit_ana.total_files_modified == 32

    # 5. Validate contributors (must be 2)
    assert len(repo.contributors) == 2
    contributor_pepe = next(c for c in repo.contributors if c.github_user == "PepeM112")
    assert contributor_pepe.contributions == 97
    assert "avatars.githubusercontent.com" in contributor_pepe.avatar


def test_mapping_consistency_null_fields() -> None:
    """Validate that if optional fields are missing, the system does not break (Robustness)."""
    analysis = get_analysis_details(1)
    assert analysis is not None
    assert analysis.repo is not None
    assert analysis.repo.description is None or analysis.repo.description == ""
