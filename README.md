# PyCEFR

**Analyse Python repositories and classify code constructs using CEFR-inspired proficiency levels (A1 - C2).**

PyCEFR parses the AST of every Python file in a project and maps each language construct (list comprehensions, decorators, generators, metaclasses, etc.) to a proficiency level inspired by the [Common European Framework of Reference for Languages](https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages). The result is a per-file and per-contributor breakdown showing how "advanced" the codebase is.

---

## Features

- Analyse any public GitHub repository by URL
- Classify ~93 Python language constructs into levels A1 through C2
- Per-contributor statistics: commits, lines of code, estimated development hours
- Interactive dashboard with charts (bar, radar, doughnut, treemap)
- File-level drill-down with level filtering
- Export / import analyses as JSON
- CLI mode for local directories and GitHub repos

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Pydantic v2, SQLite |
| Frontend | Vue 3 (Composition API), TypeScript, Vuetify 3, Chart.js |
| Tooling | Vite, ESLint, Prettier, Stylelint, Husky, Vitest |
| API Client | Auto-generated from OpenAPI via `@hey-api/openapi-ts` |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [GitHub personal access token](https://github.com/settings/tokens) (for API validation calls)

### 1. Clone and install

```bash
git clone https://github.com/<your-org>/pycefr.git
cd pycefr
make setup
```

This creates a Python virtual environment (`.venv/`), installs backend dependencies, installs frontend npm packages, and initialises the SQLite database.

### 2. Configure environment

Create a `.env` file in the project root:

```env
API_KEY=ghp_your_github_token_here
```

Optional settings (with defaults):

```env
IGNORE_FOLDERS=node_modules,myenv,.git,__pycache__
PYTHON_THRESHOLD_PERCENTAGE=30
DATABASE_PATH=database/pycefr.db
ADD_LOCAL_SUFFIX=true
AUTO_DISPLAY_CONSOLE=true
```

| Variable | Description |
|---|---|
| `IGNORE_FOLDERS` | Comma-separated folder names excluded from analysis |
| `PYTHON_THRESHOLD_PERCENTAGE` | Minimum % of Python code required in a repo to allow analysis |
| `DATABASE_PATH` | Path to the SQLite database file |
| `ADD_LOCAL_SUFFIX` | Append `_local` suffix to result files for local analyses, avoiding overwrites |
| `AUTO_DISPLAY_CONSOLE` | Automatically print results to the console after finishing an analysis |

### 3. Run

Start both servers:

```bash
# Terminal 1 — Backend (http://localhost:8000)
make up-backend

# Terminal 2 — Frontend (http://localhost:5173)
make up-frontend
```

Or run everything at once:

```bash
make run-all
```

### 4. Open the app

Navigate to [http://localhost:5173](http://localhost:5173), paste a GitHub repository URL, and start an analysis.

## CLI Usage

PyCEFR also works as a command-line tool:

```bash
# Analyse a GitHub repository
.venv/bin/python pycefr.py --repo https://github.com/user/repo

# Analyse a GitHub user (choose from their public repos)
.venv/bin/python pycefr.py --user username

# Analyse a local directory
.venv/bin/python pycefr.py --directory /path/to/project

# List previous results
.venv/bin/python pycefr.py --list

# Display results in console
.venv/bin/python pycefr.py --console results/result_file.json
```

## Development

### Useful commands

```bash
make help            # Show all available commands
make test            # Run backend tests (pytest)
make init-db         # Reset and recreate the database
make seed            # Populate database with test data
make gen-ts          # Regenerate TypeScript client from OpenAPI schema
make clean           # Remove .venv, generated clients, and database
```

### Frontend linting and formatting

```bash
cd frontend-vue
npm run lint         # ESLint (auto-fix)
npm run format       # Prettier
npm run type-check   # vue-tsc
npm run test         # Vitest
```

### Backend linting

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy .
```

## Project Structure

```
pycefr/
  backend/
    api/               # FastAPI route handlers
    config/            # Pydantic settings
    db/                # SQLite schema, CRUD utilities
    models/schemas/    # Pydantic models (analysis, repo, common)
    services/analyzer/ # Core analysis engine
      analyzer.py        # CLI orchestrator
      analyzer_class.py  # AST walker and file scanner
      levels.py          # AST node -> CEFR ClassId mapping (the brain)
      git_local_manager.py  # Local .git metadata reader
      github_manager.py    # GitHub REST API client
    main.py            # FastAPI app entry point
  frontend-vue/
    src/
      client/          # Auto-generated OpenAPI client (do not edit)
      components/      # Vue components
      composables/     # Reusable composition functions
      plugins/         # Vuetify, i18n, router setup
      utils/           # Helpers (charts, date formatting, enums)
      views/           # Page-level components
  database/            # SQLite database file (gitignored)
  pycefr.py            # CLI entry point
  Makefile             # Build and run commands
  pyproject.toml       # Python project metadata and tool config
```

## How It Works

1. **Validation** — The GitHub URL is checked for existence and Python language percentage (default threshold: 20%).
2. **Cloning** — The repository is cloned into a temporary directory.
3. **AST Analysis** — Every `.py` file is parsed. Each AST node is classified into one of ~93 construct categories (e.g. `COMPREHENSION_LIST`, `DECORATOR_CLASSMETHOD`, `EXCEPTION_CUSTOM`), each mapped to a CEFR level.
4. **Git Metadata** — Contributor stats (commits, LOC, estimated hours) are extracted directly from the local `.git` folder — no paginated API calls.
5. **Results** — The analysis is stored in SQLite and displayed in the dashboard with interactive charts and file-level breakdowns.

## Licence

<!-- TODO: Add licence -->
