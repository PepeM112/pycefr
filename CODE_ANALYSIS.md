# PyCEFR — Code Analysis

Full codebase review (backend + frontend). Findings are grouped by severity.

---

## Bugs

### 1. `staticmethod` / `classmethod` ClassId swap — `levels.py:299-302`

The decorator classification is inverted: `staticmethod` maps to `ClassId.STATIC_CLASSMETHOD` and `classmethod` maps to `ClassId.STATIC_STATICMETHOD`. This silently produces wrong CEFR classifications for every analysed repo.

```python
# Current (wrong)
if decorator.id == "staticmethod":
    features.append(ClassId.STATIC_CLASSMETHOD)
elif decorator.id == "classmethod":
    features.append(ClassId.STATIC_STATICMETHOD)

# Correct
if decorator.id == "staticmethod":
    features.append(ClassId.STATIC_STATICMETHOD)
elif decorator.id == "classmethod":
    features.append(ClassId.STATIC_CLASSMETHOD)
```

**Impact:** High — affects accuracy of every analysis.

### 2. Operator precedence in `db_utils.py:237-239`

The `or` expression binds incorrectly due to missing parentheses:

```python
profile_url=row["repo_owner_profile_url"] or f"https://github.com/{row['repo_owner_login']}"
if row["repo_owner_login"]
else "",
```

Python parses this as:
```python
profile_url = (row["repo_owner_profile_url"]) or (f"..." if row["repo_owner_login"] else "")
```

The `if/else` only applies to the fallback URL, not the whole expression. If `repo_owner_profile_url` is a non-empty string, it's used regardless of whether `repo_owner_login` exists. The intent was probably:

```python
profile_url=(
    (row["repo_owner_profile_url"] or f"https://github.com/{row['repo_owner_login']}")
    if row["repo_owner_login"]
    else ""
),
```

**Impact:** Low — in practice `profile_url` is almost always populated, but the logic is wrong.

### 3. `.py` vs `.PY` counting inconsistency — `analyzer_class.py`

`_count_python_files()` (line 200) matches `(".py", ".PY")`, but `_analyse_directory()` (line 90) only matches `".py"`. Files with uppercase extensions are counted in the progress bar denominator but never analysed, so the bar would never reach 100% if such files exist.

**Fix:** Either match `.PY` in both places or neither.

---

## Warnings

### 4. Dead code: `mainCharts` computed — `AnalysisCharts.vue:227-231`

The `mainCharts` computed property is defined but never referenced in the template or anywhere else. It duplicates data already present in `charts`.

### 5. Duplicate `getStatusColor` — `AnalysisCard.vue:105`

`AnalysisCard.vue` defines a local `getStatusColor` function identical to the one already exported from `utils/utils.ts` (which `AnalysesView.vue` imports correctly). Replace the local copy with an import.

### 6. Hardcoded Spanish locale — `datetime.ts:8`

```typescript
dayjs.locale('es');
```

The project uses `vue-i18n` for internationalisation, but date formatting is permanently set to Spanish. This should read from the current i18n locale so dates match the user's language selection.

### 7. `Sorting` type defined locally — `useSorting.ts:6-8`

```typescript
// Should be created in backend
export type Sorting = {
  column: string;
  direction: SortDirection;
};
```

The comment acknowledges it. The backend already has a `Sorting` schema in `common.py` — it should be exposed in the OpenAPI spec so the frontend client auto-generates it, instead of maintaining a manual copy.

### 8. Widespread `any` usage in frontend

The project's coding standards explicitly forbid `any`, yet it appears in ~30 places (excluding auto-generated client and test files where `as any` is used for deliberate invalid-input testing). Notable offenders:

| File | Lines | Note |
|---|---|---|
| `utils/enums.ts` | 11, 15, 42 | Core utility — should use generics |
| `utils/filter.ts` | 8, 12, 19, 181 | Type guards use `any` param — should be `unknown` |
| `types/fetcher.ts` | 20 | `values?: any` |
| `composables/useRules.ts` | 6, 14 | Validation rules — should be `unknown` or `string` |
| `composables/useQuery.ts` | 33-34 | `as any` cast on router failure |
| `plugins/vuetify.ts` | 17 | Icon component props |
| `AnalysisCharts.vue` | 169, 173, 290 | Chart tooltip callbacks and treemap data |

### 9. No `.env.example` or environment documentation

The backend requires a `.env` file with at least `API_KEY` (GitHub token). The old README references a JSON-format `.env` that no longer applies — the project now uses `pydantic-settings` with standard `KEY=VALUE` format. New contributors have no way to discover required variables.

---

## Improvement Proposals

### 10. Add test coverage for `levels.py` (the classification brain)

`levels.py` is the core of the project — it maps AST nodes to CEFR classes. It has zero tests. A comprehensive test suite (~30-40 cases) would catch regressions like bug #1 above. See `.claude/TODO_TESTING.md` for a detailed test plan.

### 11. Input sanitisation on `clone_repo` URL

`GitHubManager.clone_repo()` passes `self.repo_url` directly to `subprocess.run(["git", "clone", ...])`. While the list form of `subprocess.run` avoids shell injection, the URL is not validated beyond basic format checks. A URL like `--upload-pack=...` could be passed. Adding a check that the URL starts with `https://` after parsing (which `validate_repo_url` already does, but `clone_repo` can be called independently) would harden it.

### 12. CLI entry point (`analyzer.py`) — `request_url` does not use `clone_id`

The CLI path calls `clone_repo()` and `delete_tmp_files()` without a `clone_id`, so it wipes all of `backend/tmp/`. If the web server and CLI run simultaneously against the same machine, the CLI cleanup would destroy in-progress web analyses. Consider generating a random ID for CLI runs too.

### 13. Error handling in `run_full_analysis_process` — silent failures

When the background task fails, `mark_analysis_as_failed()` is called but the user only sees `FAILED` status without actionable details. The error string `f"Internal Error: {e}"` may expose internal paths. Consider:
- Logging the full traceback at `ERROR` level (already done).
- Storing a sanitised user-facing message in the DB.

### 14. Frontend — no loading/error states for chart data

`AnalysisCharts.vue` assumes `props.analysis.fileClasses` is always populated. If the analysis completed with zero Python files (edge case), several chart computations would produce empty datasets without any user feedback. A simple "No data to display" fallback in the template would improve UX.

### 15. Frontend — `AnalysisDetailsView` polls until completion

The detail view currently loads once. If a user navigates to a still-in-progress analysis, they see `IN_PROGRESS` with no way to see updates without manually refreshing. Consider polling or SSE for live status updates.

### 16. `db_utils.py` — raw SQL with string interpolation

While the main query builders use parameterised queries correctly, the dynamic filter construction in `get_analyses()` builds `WHERE` clauses by appending strings. The values are passed as parameters, but the column/direction names come from enums that are not parameterised (they're inserted directly into the SQL string). This is safe as long as the enums stay controlled, but would be cleaner with a whitelist validation step.

### 17. `GitLocalManager.get_remote_url()` duplicates `GitHubManager.get_git_repo_url()`

Both methods read `.git/config` to extract the remote origin URL. `GitLocalManager` handles SSH URL conversion slightly differently (uses `.removesuffix(".git")` vs `.replace(".git", "")`). They should share one implementation to avoid drift.

### 18. Frontend date format `DD-MM-YYYY` may confuse US users

The default format in `datetime.ts` is `DD-MM-YYYY` (European). Combined with the hardcoded Spanish locale (#6), this works for the current user base but would need attention for internationalisation.

---

## Minor / Style

- `AnalysisCard.vue` uses `@` alias imports for some but not all references — consistent import style would help.
- `frontend-vue/package.json` version is `0.0.0` — consider bumping to `0.1.0` to match `pyproject.toml`.
- The `backend/main.py` CORS config allows `*` origins — fine for development but should be locked down for production.
- `analyzer_class.py` progress bar uses raw ANSI escape codes (`\033[K`, `\r`) — works in terminals but can produce garbage in log files or non-TTY contexts. Consider guarding with `sys.stdout.isatty()`.
