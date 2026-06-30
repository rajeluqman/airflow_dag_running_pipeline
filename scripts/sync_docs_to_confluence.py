"""Publish the curated onboarding doc set to Confluence as living documentation.

Ported from CIL (architecture/control_plane_lab/_source_to_port/sync_docs_to_confluence.py),
philosophy only: the PUBLISH_SET below is this repo's own curated set (a newcomer's reading
order through the control-plane/teaching-lab/chaos-range identity), not a 1:1 mirror of
architecture/*.md. This repo gets its own Confluence space (owner's original ask — one space
per repo).

Confluence Cloud REST API only (Basic Auth: email + API token). Markdown -> HTML via the
`markdown` package; posted as Confluence "storage"-representation content. An existing page is
found by title and updated (version-incremented), never duplicated.

Deliberately EXCLUDED from Confluence: the 10 individual ADR pages under architecture/ADR/
(replaced by the consolidated confluence/01_ARCHITECTURE_DECISIONS.md hub page) and
architecture/REPO_MAP.md (dev navigation, not onboarding). Those stay in the repo as source of
truth.

Manual run only today — NOT wired into CI or any Airflow DAG (same rationale as the CIL
original: a doc-publish step has no business being a hard CI gate or a triggered DAG task).

Usage:
    python scripts/sync_docs_to_confluence.py             # real run, needs the 5 env vars
    python scripts/sync_docs_to_confluence.py --dry-run    # render + list, no API calls, no creds
    python scripts/sync_docs_to_confluence.py --prune       # also DELETE live pages no longer in the
                                                            # curated set
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
PROJECT_PREFIX = "Control-Plane Airflow Lab"

REQUIRED_ENV = [
    "CONFLUENCE_BASE_URL",  # e.g. https://yourcompany.atlassian.net/wiki
    "CONFLUENCE_EMAIL",
    "CONFLUENCE_API_TOKEN",
    "CONFLUENCE_SPACE_KEY",
    "CONFLUENCE_PARENT_PAGE_ID",
]

# Curated onboarding set, in reading order. (repo-relative path, explicit page-name or None).
# None -> the page name is the file stem (keeps idempotency with already-created pages).
PUBLISH_SET: list[tuple[str, str | None]] = [
    ("confluence/00_START_HERE.md", "Start Here"),
    # 1. What this repo orchestrates
    ("architecture/REPO_REGISTRY.md", None),
    ("architecture/CROSS_STACK_CONTRACT.md", None),
    ("architecture/SECRETS_BACKEND.md", None),
    # 2. Architecture decisions (consolidated hub — individual ADR pages are NOT published)
    ("confluence/01_ARCHITECTURE_DECISIONS.md", "Architecture Decisions"),
    # 3. Teaching path
    ("learning/CURRICULUM.md", None),
    # 4. Chaos-range skeleton
    ("simulation/ISOLATION_CONTRACT.md", None),
    ("simulation/MTTR_SCORECARD.md", None),
    # 5. Detailed build log
    ("PROJECT_STATUS.md", None),
]


def _page_title(rel_path: str, name: str | None) -> str:
    stem = name if name is not None else Path(rel_path).stem
    return f"{PROJECT_PREFIX} — {stem}"


def _published() -> list[tuple[Path, str]]:
    """(absolute path, page title) for every doc in the curated set that exists on disk."""
    out: list[tuple[Path, str]] = []
    for rel, name in PUBLISH_SET:
        p = REPO_DIR / rel
        if not p.exists():
            sys.exit(f"sync_docs_to_confluence: curated doc missing on disk: {rel}")
        out.append((p, _page_title(rel, name)))
    return out


def _to_confluence_storage_html(md_text: str) -> str:
    import markdown
    return markdown.markdown(md_text, extensions=["tables", "fenced_code"])


def _assert_env(env: dict[str, str]) -> None:
    missing = [k for k in REQUIRED_ENV if not env.get(k)]
    if missing:
        sys.exit(
            f"sync_docs_to_confluence: missing required env var(s): {', '.join(missing)} — "
            "refusing to run. Use --dry-run to preview without credentials."
        )


def _find_existing_page(base_url: str, auth, space_key: str, title: str) -> dict | None:
    import requests
    resp = requests.get(
        f"{base_url}/rest/api/content",
        params={"title": title, "spaceKey": space_key, "expand": "version"},
        auth=auth,
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


# Our doc pages are ALL titled "<PROJECT_PREFIX> — <stem>". The bare space homepage is titled
# just PROJECT_PREFIX (no separator), so the separator is what distinguishes a prunable doc page
# from the homepage/parent — match on the full prefix-with-separator, never the bare prefix.
TITLE_PREFIX = f"{PROJECT_PREFIX} — "


def _list_project_pages(base_url: str, auth, space_key: str) -> list[dict]:
    """Every page in the space that is one of OUR doc pages (prefix + ' — '), paged."""
    import requests
    pages: list[dict] = []
    start = 0
    while True:
        resp = requests.get(
            f"{base_url}/rest/api/content",
            params={"spaceKey": space_key, "type": "page", "limit": 100, "start": start},
            auth=auth,
            timeout=30,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        pages += [p for p in results if p.get("title", "").startswith(TITLE_PREFIX)]
        if len(results) < 100:
            return pages
        start += 100


def _create_page(base_url: str, auth, space_key: str, parent_id: str, title: str, html: str) -> str:
    import requests
    resp = requests.post(
        f"{base_url}/rest/api/content",
        auth=auth,
        json={
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "ancestors": [{"id": parent_id}],
            "body": {"storage": {"value": html, "representation": "storage"}},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _update_page(base_url: str, auth, page_id: str, next_version: int, title: str, html: str) -> None:
    import requests
    resp = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        auth=auth,
        json={
            "type": "page",
            "title": title,
            "version": {"number": next_version},
            "body": {"storage": {"value": html, "representation": "storage"}},
        },
        timeout=30,
    )
    resp.raise_for_status()


def _delete_page(base_url: str, auth, page_id: str) -> None:
    import requests
    resp = requests.delete(f"{base_url}/rest/api/content/{page_id}", auth=auth, timeout=30)
    resp.raise_for_status()


def sync(env: dict[str, str], dry_run: bool, prune: bool) -> None:
    docs = _published()
    keep_titles = {title for _, title in docs}

    if dry_run:
        print(f"[dry-run] would publish {len(docs)} curated doc(s) — no API calls made:")
        for path, title in docs:
            html = _to_confluence_storage_html(path.read_text())
            print(f"  + {title}  ({len(html)} chars, from {path.relative_to(REPO_DIR)})")
        return

    _assert_env(env)
    base_url = env["CONFLUENCE_BASE_URL"].rstrip("/")
    auth = (env["CONFLUENCE_EMAIL"], env["CONFLUENCE_API_TOKEN"])
    space_key = env["CONFLUENCE_SPACE_KEY"]
    parent_id = env["CONFLUENCE_PARENT_PAGE_ID"]

    for path, title in docs:
        html = _to_confluence_storage_html(path.read_text())
        existing = _find_existing_page(base_url, auth, space_key, title)
        if existing:
            next_version = existing["version"]["number"] + 1
            _update_page(base_url, auth, existing["id"], next_version, title, html)
            print(f"updated: {title} (v{next_version})")
        else:
            page_id = _create_page(base_url, auth, space_key, parent_id, title, html)
            print(f"created: {title} (id={page_id})")

    if prune:
        live = _list_project_pages(base_url, auth, space_key)
        orphans = [p for p in live if p["title"] not in keep_titles and p["id"] != parent_id]
        print(f"\n--prune: {len(orphans)} live page(s) not in the curated set — deleting:")
        for p in orphans:
            _delete_page(base_url, auth, p["id"])
            print(f"  deleted: {p['title']} (id={p['id']})")


if __name__ == "__main__":
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="render + list pages, no API calls, no credentials required"
    )
    parser.add_argument(
        "--prune", action="store_true", help="DELETE live pages (PROJECT_PREFIX) no longer in the curated set"
    )
    args = parser.parse_args()
    sync(dict(os.environ), args.dry_run, args.prune)
