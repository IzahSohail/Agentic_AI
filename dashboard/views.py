import re

import requests
from django.conf import settings
from django.shortcuts import render


def get_headers():
    """Build GitHub API request headers using the configured token."""
    token = settings.GITHUB_TOKEN
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def get_copilot_prs(repo):
    """
    Retrieve PRs authored by GitHub Copilot via GitHub Search API.
    Equivalent to website query: is:pr author:@copilot (scoped to repo).
    """
    headers = get_headers()
    if not headers:
        return None, "Missing GITHUB_TOKEN in .env"

    # Match the working website query exactly (plus repo scope).
    query = f"repo:{repo} is:pr is:closed author:@copilot"
    url = "https://api.github.com/search/issues"

    page = 1
    per_page = 100
    all_items = []

    while True:
        response = requests.get(
            url,
            headers=headers,
            params={"q": query, "per_page": per_page, "page": page},
            timeout=20,
        )

        if response.status_code != 200:
            return None, f"Error {response.status_code}: {response.text}"

        items = response.json().get("items", [])
        all_items.extend(items)

        if len(items) < per_page:
            break

        page += 1

    return all_items, None


def extract_session_url(pr_body):
    """Extract the Copilot Workspace session URL from a PR body, if present."""
    if not pr_body:
        return "N/A"
    # Matches the specific GitHub Workspace session link pattern
    pattern = r"(https://copilot-workspace\.githubnext\.com/[^\s\)\?\!]+)"
    match = re.search(pattern, pr_body)
    return match.group(0) if match else "N/A"


def get_pr_comments(repo, pr_number):
    """
    Fetch all comments for a specific PR.
    Returns a list of comment objects and any error.
    """
    headers = get_headers()
    if not headers:
        return None, "Missing GITHUB_TOKEN in .env"

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    page = 1
    per_page = 100
    all_comments = []

    while True:
        response = requests.get(
            url,
            headers=headers,
            params={"per_page": per_page, "page": page},
            timeout=20,
        )

        if response.status_code != 200:
            return None, f"Error {response.status_code}: {response.text}"

        comments = response.json()
        if isinstance(comments, dict):
            # GitHub returns errors as a dict
            return None, f"API Error: {comments.get('message', 'Unknown')}"

        all_comments.extend(comments)

        if len(comments) < per_page:
            break

        page += 1

    return all_comments, None


def home(request):
    """Main dashboard view: shows all Copilot PRs and comments for the latest one."""
    repo = settings.GITHUB_REPO
    prs, error = get_copilot_prs(repo)

    if error:
        return render(request, "dashboard/home.html", {"error": error})

    rows = []
    first_pr_number = None
    for pr in prs:
        user_info = pr.get("user", {})
        pr_data = {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"].upper(),
            "author": user_info.get("login", "Unknown"),
            "author_url": user_info.get("html_url", "#"),
            "date": pr.get("created_at", "")[:10],
            "session_url": extract_session_url(pr.get("body", "")),
            "pr_url": pr.get("html_url", "#"),
        }
        rows.append(pr_data)
        if first_pr_number is None:
            first_pr_number = pr["number"]

    # Sort newest PR numbers first
    rows.sort(key=lambda r: r["number"], reverse=True)

    # Fetch comments for the first (most recent) PR
    comments_data = []
    comments_error = None
    if first_pr_number:
        first_pr = next((pr for pr in prs if pr["number"] == first_pr_number), None)
        if first_pr:
            # Include the PR body as the first item in the comments section
            pr_user_info = first_pr.get("user", {})
            comments_data.append({
                "id": f"pr_{first_pr_number}",
                "author": pr_user_info.get("login", "Unknown"),
                "author_url": pr_user_info.get("html_url", "#"),
                "date": first_pr.get("created_at", "")[:10],
                "body": first_pr.get("body", ""),
                "comment_url": first_pr.get("html_url", "#"),
                "is_pr_body": True,
            })

        comments, comments_error = get_pr_comments(repo, first_pr_number)
        if comments:
            for comment in comments:
                user_info = comment.get("user", {})
                comments_data.append({
                    "id": comment.get("id"),
                    "author": user_info.get("login", "Unknown"),
                    "author_url": user_info.get("html_url", "#"),
                    "date": comment.get("created_at", "")[:10],
                    "body": comment.get("body", ""),
                    "comment_url": comment.get("html_url", "#"),
                    "is_pr_body": False,
                })

    return render(request, "dashboard/home.html", {
        "repo": repo,
        "rows": rows,
        "first_pr_number": first_pr_number,
        "comments_data": comments_data,
        "comments_error": comments_error,
    })
