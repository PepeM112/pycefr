#!/usr/bin/env python3
"""Seed the database with real analyses from well-known Python repositories."""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

SEED_REPOS = [
    {
        "repo_url": "https://github.com/django/django",
        "tags": ["web-framework", "full-stack", "large-project"],
    },
    {
        "repo_url": "https://github.com/benjaminp/six",
        "tags": ["compatibility", "utility", "lightweight"],
    },
    {
        "repo_url": "https://github.com/sqlalchemy/sqlalchemy",
        "tags": ["orm", "database", "large-project"],
    },
    {
        "repo_url": "https://github.com/Delgan/loguru",
        "tags": ["logging", "utility", "lightweight"],
    },
    {
        "repo_url": "https://github.com/jd/tenacity",
        "tags": ["retry", "utility", "lightweight"],
    },
]

POLL_INTERVAL_SECONDS = 3
MAX_WAIT_SECONDS = 600


def wait_for_backend(retries: int = 10, delay: int = 2) -> bool:
    for attempt in range(retries):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        if attempt < retries - 1:
            print(f"  Backend not ready, retrying in {delay}s... ({attempt + 1}/{retries})")
            time.sleep(delay)
    return False


def create_analysis(repo: dict) -> dict:
    response = requests.post(f"{API_URL}/analyses", json=repo, timeout=30)
    response.raise_for_status()
    return response.json()


def poll_until_done(analysis_id: int) -> dict | None:
    start = time.time()
    while time.time() - start < MAX_WAIT_SECONDS:
        response = requests.get(f"{API_URL}/analyses/{analysis_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["status"] in ("completed", "failed"):
            return data
        time.sleep(POLL_INTERVAL_SECONDS)
    return None


def main() -> None:
    print("PyCEFR Seed — Populating database with real analyses\n")

    print("Checking backend availability...")
    if not wait_for_backend():
        print("ERROR: Backend is not running. Start it with 'make up-backend' first.")
        sys.exit(1)
    print("Backend is ready.\n")

    print(f"Triggering {len(SEED_REPOS)} analyses...")
    pending = []
    for repo in SEED_REPOS:
        result = create_analysis(repo)
        analysis_id = result["id"]
        name = result["name"]
        print(f"  #{analysis_id} {name} — triggered")
        pending.append({"id": analysis_id, "name": name, "start": time.time()})

    print(f"\nWaiting for all analyses to complete (polling every {POLL_INTERVAL_SECONDS}s)...\n")

    results = []
    with ThreadPoolExecutor(max_workers=len(pending)) as executor:
        future_to_analysis = {executor.submit(poll_until_done, a["id"]): a for a in pending}
        for future in as_completed(future_to_analysis):
            analysis = future_to_analysis[future]
            data = future.result()
            elapsed = time.time() - analysis["start"]
            analysis_status = "TIMEOUT" if data is None else data["status"].upper()
            results.append(
                {"name": analysis["name"], "id": analysis["id"], "status": analysis_status, "elapsed": elapsed}
            )
            print(f"  #{analysis['id']} {analysis['name']} — {analysis_status} ({elapsed:.1f}s)")

    print("\n" + "=" * 50)
    completed = sum(1 for r in results if r["status"] == "COMPLETED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    timed_out = sum(1 for r in results if r["status"] == "TIMEOUT")
    print(f"Done: {completed} completed, {failed} failed, {timed_out} timed out")

    if failed or timed_out:
        sys.exit(1)


if __name__ == "__main__":
    main()
