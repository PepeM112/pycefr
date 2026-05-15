# PyCEFR — Code Analysis

Full codebase review (backend + frontend). Findings are grouped by severity.

Items resolved in PYCEFR-41: bugs 1-3, warnings 4-9, improvements 10-14, 16-17, and all minor/style items.

---

## Deferred — Planned for dedicated tasks

### 1. Frontend — `AnalysisDetailsView` polls until completion

The detail view currently loads once. If a user navigates to a still-in-progress analysis, they see `IN_PROGRESS` with no way to see updates without manually refreshing.

**Status:** Deferred for a dedicated task. SSE (Server-Sent Events) is the preferred approach over WebSockets since the data flow is unidirectional (server → client).

**Proposed approach:**

1. **Backend — SSE endpoint:** Add a `GET /api/analyses/{id}/stream` endpoint using FastAPI's `StreamingResponse` with `text/event-stream` content type. The endpoint polls the DB at a short interval (e.g. 2-3s) and emits status events (`IN_PROGRESS`, `COMPLETED`, `FAILED`) until the analysis finishes, then closes the stream.

2. **Frontend — EventSource composable:** Create a `useAnalysisStream(analysisId)` composable that opens an `EventSource` connection to the SSE endpoint. On `COMPLETED`, it triggers a full data refetch and closes the connection. On `FAILED`, it displays the error and closes. Include automatic reconnection logic and cleanup on component unmount.

3. **UX:** While `IN_PROGRESS`, show a progress indicator (existing `v-progress-linear`) with the status message from the stream. Transition to the full detail view once `COMPLETED` arrives.

4. **Considerations:**
   - SSE is simpler than WebSockets: no handshake upgrade, works through most proxies, auto-reconnects natively via `EventSource`.
   - The background task could optionally emit progress events (e.g. "Cloning...", "Analysing file 12/50...") by writing intermediate status to the DB.
   - Connection timeout: close the stream server-side after a max duration (e.g. 10 minutes) to avoid hanging connections.

### 2. Frontend — Settings page (date format, language, theme)

The default date format in `datetime.ts` is `DD-MM-YYYY` (European), which may confuse non-European users. Addressing this properly requires a Settings page where users can configure preferences (date format, language, theme). Language and theme toggles already exist in-place; a Settings page would consolidate them and add date format selection.

---

## Architectural Observations

### 3. `db_utils.py` is a 660-line bag of functions with no abstraction over the DB

Every function opens a connection, writes raw SQL, manually maps `sqlite3.Row` to Pydantic models, and closes the connection. There is a lot of row-to-model boilerplate repeated across `get_analyses`, `get_analysis_details`, `create_empty_analysis`, `update_analysis_results`, etc.

If SQLite is staying, a lightweight repository pattern would help — even just a class that holds the connection and has typed methods. If the project ever switches to PostgreSQL (e.g. for a Vercel demo), every function would need to be rewritten. An ORM like SQLAlchemy (or even a thin abstraction layer) would make that migration trivial and cut `db_utils.py` in half.

**Priority:** Medium — this is where technical debt accumulates fastest as new features are added.

### 4. `analyzer.py` naming is confusing alongside `analyzer_class.py`

- `analyzer.py` — CLI entry points (`request_url`, `run_directory`, `run_user`)
- `analyzer_class.py` — the `Analyzer` class (AST walking, progress bar)

The name `analyzer.py` suggests it is the analyzer, but it is really the CLI orchestrator. Renaming to `cli.py` (or `cli_commands.py`) would make the distinction obvious. `analyzer_class.py` could then become `analyzer.py`.

**Priority:** Low — naming only, no logic change.

### 5. `analysis_routes.py` mixes HTTP concerns with business logic

`run_full_analysis_process` (line 291) is a ~40-line function that clones, analyzes, fetches git metadata, and writes to the DB. It lives in the routes file but has nothing to do with HTTP. It is essentially the same orchestration as `request_url` in `analyzer.py`, but for the web path. Both duplicate the clone → analyze → enrich → save flow.

Extracting a shared `run_analysis(repo_url, analysis_id=None)` service function that both CLI and API call would remove duplication and make `analysis_routes.py` purely about HTTP request/response handling.

**Priority:** Medium — reduces duplication and makes both paths easier to maintain.

### 6. `run_directory` cleanup asymmetry

`run_directory` calls `Analyzer.delete_tmp_files()` in its `finally` block without a `clone_id`, so it deletes everything in `backend/tmp/`. If `run_directory` detects a git remote and delegates to `request_url` (which now uses its own `clone_id`), then `request_url` does its own scoped cleanup — and `run_directory`'s `finally` would also try to nuke all of `backend/tmp/`, potentially racing with concurrent web analyses.

The `finally` in `run_directory` should only clean up when it did not delegate to `request_url`.

**Priority:** Low — only matters if CLI and web server run simultaneously on the same machine.

### 7. Frontend — `AnalysisDetailsView.vue` does too much in one component

At 360 lines with chart data computation, file tree wiring, table filtering, level toggling, menu actions, and data fetching, it is heading toward "monolith view" territory. The chart data preparation and the table filtering logic are good candidates for composables (`useAnalysisCharts`, `useAnalysisTable`), keeping the view as a layout orchestrator.

**Priority:** Low — manageable now but will grow with new features.

### 8. No migration strategy for the database

The DB schema appears to be created inline or via a setup script. As the project evolves (new columns, new tables for settings, etc.), there is no versioned migration system. Something like Alembic or a simple numbered SQL migration folder would prevent manual intervention on existing databases when the schema changes.

**Priority:** Medium — becomes critical as soon as users have persistent data they don't want to lose on updates.
