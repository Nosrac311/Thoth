import base64
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_OWNER = os.getenv("GITHUB_OWNER", "Nosrac311")
GITHUB_REPO = os.getenv("GITHUB_REPO", "Thoth")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

# Fine-grained GitHub Personal Access Token.
#
# Required repository permission:
#   Contents -> Read and write
#
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# SQLite database used by Thoth.
DATABASE_PATH = (
    Path(__file__).resolve().parent
    / "database"
    / "inspections.db"
)

# Optional JSON exports.
DATA_DIRECTORY = "data/inspections"

API_VERSION = "2026-03-10"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def _api_request(
    method,
    endpoint,
    payload=None,
):
    """
    Make an authenticated request to the GitHub REST API.

    Returns:
        dict
    """

    if not GITHUB_TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN is not set. "
            "GitHub synchronization cannot run."
        )

    url = (
        f"https://api.github.com"
        f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"{endpoint}"
    )

    body = None

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "Thoth-Inspection-Monitor",
            "Content-Type": "application/json",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:

            raw = response.read()

            if not raw:
                return {}

            return json.loads(
                raw.decode("utf-8")
            )

    except urllib.error.HTTPError as exc:

        error_body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"GitHub API error {exc.code}: {error_body}"
        ) from exc


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def _checkpoint_database():
    """
    Checkpoint the SQLite WAL so all committed changes are
    safely represented in inspections.db before uploading it.

    This is important because the application uses:

        PRAGMA journal_mode=WAL;

    Without checkpointing, some recent database changes could
    still be sitting in inspections.db-wal rather than the
    main inspections.db file.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    try:

        connection.execute(
            "PRAGMA wal_checkpoint(TRUNCATE)"
        )

    finally:

        connection.close()


def _get_local_inspection_count():
    """
    Return the number of inspections in the local SQLite database.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    try:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM inspections"
        )

        return cursor.fetchone()[0]

    finally:

        connection.close()


def _load_inspections():
    """
    Read all inspections from SQLite.

    Returns:
        dict[str, list[dict]]
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                state_id,
                inspection_date,
                restaurant,
                inspector_id,
                score,
                grade,
                source
            FROM inspections
            ORDER BY
                source ASC,
                inspection_date DESC,
                restaurant ASC
            """
        )

        rows = cursor.fetchall()

    finally:

        connection.close()

    inspections_by_source = {}

    for row in rows:

        source = row["source"]

        inspections_by_source.setdefault(
            source,
            []
        ).append(
            {
                "id": row["state_id"],
                "date": row["inspection_date"],
                "name": row["restaurant"],
                "inspector_id": row["inspector_id"],
                "score": row["score"],
                "grade": row["grade"],
                "source": row["source"],
            }
        )

    return inspections_by_source


# ---------------------------------------------------------------------------
# JSON export helpers
# ---------------------------------------------------------------------------

def _slugify_source(source):
    """
    Convert a source name into a safe filename.
    """

    value = str(source).strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    )

    value = value.strip("-")

    return value or "unknown"


def _make_json(inspections):
    """
    Create deterministic JSON.
    """

    return (
        json.dumps(
            inspections,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _get_branch():
    """
    Get the current branch reference.
    """

    encoded_branch = urllib.parse.quote(
        GITHUB_BRANCH,
        safe="",
    )

    return _api_request(
        "GET",
        f"/git/ref/heads/{encoded_branch}",
    )


def _get_commit(commit_sha):
    """
    Get a Git commit.
    """

    return _api_request(
        "GET",
        f"/git/commits/{commit_sha}",
    )


def _create_text_blob(content):
    """
    Create a UTF-8 text Git blob.
    """

    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode("ascii")

    response = _api_request(
        "POST",
        "/git/blobs",
        {
            "content": encoded,
            "encoding": "base64",
        },
    )

    return response["sha"]


def _create_binary_blob(file_path):
    """
    Create a binary Git blob.

    Used for the SQLite database.
    """

    with open(
        file_path,
        "rb",
    ) as file:

        content = file.read()

    encoded = base64.b64encode(
        content
    ).decode("ascii")

    response = _api_request(
        "POST",
        "/git/blobs",
        {
            "content": encoded,
            "encoding": "base64",
        },
    )

    return response["sha"]


def _create_tree(
    base_tree_sha,
    files,
):
    """
    Create a Git tree containing the files.

    Existing files not mentioned here remain in the tree
    because base_tree is used.
    """

    entries = []

    for item in files:

        entries.append(
            {
                "path": item["path"],
                "mode": "100644",
                "type": "blob",
                "sha": item["sha"],
            }
        )

    response = _api_request(
        "POST",
        "/git/trees",
        {
            "base_tree": base_tree_sha,
            "tree": entries,
        },
    )

    return response["sha"]


def _get_existing_tree_entry(
    tree_sha,
    path,
):
    """
    Find an existing file in the Git tree.

    Returns:
        blob SHA or None
    """

    tree = _api_request(
        "GET",
        f"/git/trees/{tree_sha}?recursive=1",
    )

    for item in tree.get("tree", []):

        if item.get("path") == path:

            return item.get("sha")

    return None


def _create_commit(
    tree_sha,
    parent_sha,
    message,
):
    """
    Create a Git commit.
    """

    response = _api_request(
        "POST",
        "/git/commits",
        {
            "message": message,
            "tree": tree_sha,
            "parents": [
                parent_sha
            ],
        },
    )

    return response["sha"]


def _update_branch(commit_sha):
    """
    Move main forward.

    force=False prevents overwriting another push.
    """

    encoded_branch = urllib.parse.quote(
        GITHUB_BRANCH,
        safe="",
    )

    return _api_request(
        "PATCH",
        f"/git/refs/heads/{encoded_branch}",
        {
            "sha": commit_sha,
            "force": False,
        },
    )


# ---------------------------------------------------------------------------
# Build files
# ---------------------------------------------------------------------------

def _build_files():
    """
    Build the files that should be committed.

    Includes:

        database/inspections.db

    and:

        data/inspections/*.json
    """

    inspections_by_source = _load_inspections()

    files = []

    # -------------------------------------------------------
    # SQLite database
    # -------------------------------------------------------

    database_blob = _create_binary_blob(
        DATABASE_PATH
    )

    files.append(
        {
            "path": "database/inspections.db",
            "sha": database_blob,
        }
    )

    # -------------------------------------------------------
    # JSON exports
    # -------------------------------------------------------

    for source, inspections in sorted(
        inspections_by_source.items()
    ):

        filename = (
            f"{_slugify_source(source)}.json"
        )

        path = (
            f"{DATA_DIRECTORY}/{filename}"
        )

        content = _make_json(
            inspections
        )

        blob_sha = _create_text_blob(
            content
        )

        files.append(
            {
                "path": path,
                "sha": blob_sha,
            }
        )

    return (
        files,
        inspections_by_source,
    )


# ---------------------------------------------------------------------------
# Public synchronization function
# ---------------------------------------------------------------------------

def sync_inspections_to_github():
    """
    Synchronize the local SQLite database and JSON exports
    to GitHub.

    The SQLite database is the authoritative data source.

    Returns:
        dict
    """

    if not GITHUB_TOKEN:

        print(
            "⚠️ GITHUB_TOKEN is not configured. "
            "Skipping GitHub sync."
        )

        return {
            "success": False,
            "skipped": True,
            "reason": "missing_token",
        }

    if not DATABASE_PATH.exists():

        raise FileNotFoundError(
            f"SQLite database not found: {DATABASE_PATH}"
        )

    # -------------------------------------------------------
    # Make sure WAL changes are inside inspections.db
    # -------------------------------------------------------

    print(
        "💾 Checkpointing SQLite database..."
    )

    _checkpoint_database()

    # -------------------------------------------------------
    # Count inspections
    # -------------------------------------------------------

    local_count = _get_local_inspection_count()

    print(
        f"📊 Local SQLite database: "
        f"{local_count} inspections"
    )

    if local_count == 0:

        print(
            "ℹ️ Database contains no inspections. "
            "Skipping GitHub sync."
        )

        return {
            "success": True,
            "skipped": True,
            "reason": "no_inspections",
        }

    # -------------------------------------------------------
    # Retry if another process changes main
    # -------------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            print(
                f"🔄 GitHub sync attempt "
                f"{attempt}/{MAX_RETRIES}"
            )

            # ---------------------------------------------------
            # Get current main
            # ---------------------------------------------------

            branch = _get_branch()

            parent_sha = (
                branch["object"]["sha"]
            )

            parent_commit = _get_commit(
                parent_sha
            )

            base_tree_sha = (
                parent_commit["tree"]["sha"]
            )

            # ---------------------------------------------------
            # Build database + JSON blobs
            # ---------------------------------------------------

            files, inspections_by_source = (
                _build_files()
            )

            # ---------------------------------------------------
            # Check whether database changed
            # ---------------------------------------------------

            existing_database_sha = (
                _get_existing_tree_entry(
                    base_tree_sha,
                    "database/inspections.db",
                )
            )

            new_database_sha = next(
                item["sha"]
                for item in files
                if item["path"]
                == "database/inspections.db"
            )

            if (
                existing_database_sha
                == new_database_sha
            ):

                print(
                    "ℹ️ SQLite database has not changed. "
                    "Skipping GitHub commit."
                )

                return {
                    "success": True,
                    "skipped": True,
                    "reason": "unchanged",
                    "inspections": local_count,
                }

            # ---------------------------------------------------
            # Create new Git tree
            # ---------------------------------------------------

            tree_sha = _create_tree(
                base_tree_sha,
                files,
            )

            # ---------------------------------------------------
            # Commit message
            # ---------------------------------------------------

            source_count = len(
                inspections_by_source
            )

            timestamp = datetime.now(
                timezone.utc
            ).strftime(
                "%Y-%m-%d %H:%M UTC"
            )

            commit_message = (
                f"Update inspection database "
                f"({local_count} inspections) - "
                f"{timestamp}"
            )

            # ---------------------------------------------------
            # Create commit
            # ---------------------------------------------------

            commit_sha = _create_commit(
                tree_sha,
                parent_sha,
                commit_message,
            )

            # ---------------------------------------------------
            # Move main forward
            # ---------------------------------------------------

            _update_branch(
                commit_sha
            )

            print(
                "✅ GitHub updated successfully."
            )

            print(
                f"   Inspections: {local_count}"
            )

            print(
                f"   Sources: {source_count}"
            )

            print(
                f"   Commit: {commit_sha[:7]}"
            )

            return {
                "success": True,
                "skipped": False,
                "commit": commit_sha,
                "inspections": local_count,
                "sources": source_count,
            }

        except RuntimeError as exc:

            if attempt >= MAX_RETRIES:

                print(
                    "❌ GitHub synchronization failed "
                    "after all retry attempts."
                )

                raise

            print(
                f"⚠️ Sync attempt failed: {exc}"
            )

            print(
                f"⏳ Retrying in "
                f"{RETRY_DELAY_SECONDS} seconds..."
            )

            time.sleep(
                RETRY_DELAY_SECONDS
            )

    raise RuntimeError(
        "GitHub synchronization failed."
    )
