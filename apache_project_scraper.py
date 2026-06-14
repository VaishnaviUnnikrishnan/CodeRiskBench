#!/usr/bin/env python3
"""
Fetch Apache project names and repository links directly from:
  https://projects.apache.org/json/foundation/projects.json

The JSON is a dict keyed by project slug. Each entry contains fields like:
  - name         : display name
  - repository   : list of repo URLs (git, svn, github, etc.)
  - homepage     : project website

Output: apache_projects.json
"""

import json
import requests

SOURCE_URL = "https://projects.apache.org/json/foundation/projects.json"
OUTPUT_FILE = "apache_projects.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ApacheProjectScraper/1.0)"
}

GIT_HOSTS = (
    "github.com",
    "gitbox.apache.org",
    "git.apache.org",
    "svn.apache.org",
)


def filter_repo_links(repositories):
    """Return only recognised git/svn repo URLs from the repository list."""
    if not repositories:
        return []
    if isinstance(repositories, str):
        repositories = [repositories]
    return [r for r in repositories if any(host in r for host in GIT_HOSTS)]


def main():
    print(f"Fetching {SOURCE_URL} ...")
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    print(f"Loaded {len(raw)} projects from JSON.")

    results = []
    for slug, info in raw.items():
        name = info.get("name", slug)
        all_repos = info.get("repository", [])
        repo_links = filter_repo_links(all_repos)

        results.append({
            "slug": slug,
            "name": name,
            "homepage": info.get("homepage", ""),
            "repositories": repo_links,
        })

    # Sort alphabetically by name for readability
    results.sort(key=lambda x: x["name"].lower())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with_repos = sum(1 for r in results if r["repositories"])
    print(f"Done! {len(results)} projects saved to '{OUTPUT_FILE}'")
    print(f"Projects with at least one repo link: {with_repos}/{len(results)}")


if __name__ == "__main__":
    main()