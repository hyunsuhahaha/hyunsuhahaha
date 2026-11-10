"""Render a profile card from public GitHub data using the authenticated gh CLI."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
USER = "hyunsuhahaha"


def api(endpoint):
    result = subprocess.run(
        ["gh", "api", endpoint], check=True, capture_output=True, text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def count_search(endpoint, query):
    result = api(f"search/{endpoint}?{urlencode({'q': query, 'per_page': 1})}")
    if result.get("incomplete_results"):
        raise RuntimeError("GitHub returned incomplete search results")
    return result["total_count"]


def main():
    year = datetime.now(timezone.utc).year
    since = f"{year}-01-01"
    commits = count_search("commits", f"author:{USER} is:public committer-date:>={since}")
    prs = count_search("issues", f"author:{USER} is:public is:pr created:>={since}")
    repositories = api(f"users/{USER}")["public_repos"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="350" height="170" viewBox="0 0 350 170" role="img" aria-labelledby="title desc">
  <title id="title">GitHub public activity</title>
  <desc id="desc">{year}: {commits} public commits and {prs} public pull requests. {repositories} public repositories.</desc>
  <rect x=".5" y=".5" width="349" height="169" rx="10" fill="#0d1117" stroke="#30363d"/>
  <rect x="20" y="21" width="3" height="13" rx="1.5" fill="#f4a15b"/>
  <text x="32" y="32" fill="#f0f3f6" font-family="Segoe UI, sans-serif" font-size="14" font-weight="600">GitHub activity</text>
  <text x="330" y="32" text-anchor="end" fill="#8b949e" font-family="Consolas, monospace" font-size="11">{year}</text>
  <path d="M20 48H330" stroke="#21262d"/>
  <g fill="#b1bac4" font-family="Segoe UI, sans-serif" font-size="12">
    <text x="22" y="73">Commits</text><text x="22" y="99">Pull requests</text><text x="22" y="125">Public repositories</text>
  </g>
  <g fill="#f0f3f6" font-family="Consolas, monospace" font-size="16" font-weight="600" text-anchor="end">
    <text x="328" y="74">{commits:,}</text><text x="328" y="100">{prs:,}</text><text x="328" y="126">{repositories:,}</text>
  </g>
  <text x="22" y="151" fill="#8b949e" font-family="Consolas, monospace" font-size="9">PUBLIC DATA · COMMITS &amp; PRs IN {year}</text>
</svg>
'''
    target = ROOT / "assets/github-activity.svg"
    target.parent.mkdir(exist_ok=True)
    target.write_text(svg, encoding="utf-8")
    print(json.dumps({"year": year, "commits": commits, "pull_requests": prs, "public_repositories": repositories}))


if __name__ == "__main__":
    main()
