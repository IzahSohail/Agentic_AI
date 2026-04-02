import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, render_template_string

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "thedotmack/claude-mem"

app = Flask(__name__)

def get_headers():
    if not GITHUB_TOKEN:
        return None
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
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
    if not pr_body:
        return "N/A"
    # Matches the specific GitHub Workspace session link pattern
    pattern = r'(https://copilot-workspace\.githubnext\.com/[^\s\)\?\!]+)'
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
            # GitHub returns error as dict
            return None, f"API Error: {comments.get('message', 'Unknown')}"

        all_comments.extend(comments)

        if len(comments) < per_page:
            break

        page += 1

    return all_comments, None

@app.route("/")
def home():
    prs, error = get_copilot_prs(REPO)

    if error:
        return f"<h2>Error</h2><p style='color:red;'>{error}</p>"

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

    # Fetch comments for the first PR
    comments_data = []
    comments_error = None
    if first_pr_number:
        # Find the first PR to get its body
        first_pr = next((pr for pr in prs if pr["number"] == first_pr_number), None)
        if first_pr:
            # Add PR body as first "comment"
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

        comments, comments_error = get_pr_comments(REPO, first_pr_number)
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

    return render_template_string("""
        <html>
        <head>
            <title>Copilot PR Dashboard</title>
            <style>
                body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 40px; background-color: #f3f4f6; color: #1f2937; }
                .container { max-width: 1200px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
                header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f3f4f6; padding-bottom: 20px; }
                h2 { margin-top: 30px; margin-bottom: 15px; color: #1f2937; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #f3f4f6; }
                th { background: #f9fafb; color: #6b7280; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; }
                tr:hover { background-color: #fdfdfd; }
                .status-merged { color: #7c3aed; background: #f5f3ff; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
                .status-open { color: #059669; background: #ecfdf5; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
                .status-closed { color: #dc2626; background: #fef2f2; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
                .btn { display: inline-block; padding: 6px 12px; background: #0366d6; color: white; text-decoration: none; border-radius: 6px; font-size: 12px; transition: background 0.2s; }
                .btn:hover { background: #024ea3; }
                .author-tag { color: #0366d6; font-weight: 500; text-decoration: none; font-size: 13px; }
                .author-tag:hover { text-decoration: underline; }
                .comment-body { font-size: 13px; color: #4b5563; font-family: monospace; white-space: pre-wrap; word-break: break-word; }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <div>
                        <h1 style="margin:0;">🤖 Copilot Workspace PRs</h1>
                        <p style="color: #6b7280; margin: 5px 0 0 0;">Repo: <strong>{{ repo }}</strong></p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 24px; font-weight: bold; color: #0366d6;">{{ rows|length }}</span>
                        <p style="font-size: 12px; color: #6b7280; margin: 0;">Total Sessions</p>
                    </div>
                </header>
                <table>
                    <thead>
                        <tr>
                            <th>PR #</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Author</th>
                            <th>Title</th>
                            <th>Session URL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in rows %}
                        <tr>
                            <td><a href="{{ row.pr_url }}" target="_blank" style="font-weight:600; color:#0366d6; text-decoration:none;">#{{ row.number }}</a></td>
                            <td><span class="status-{{ row.state.lower() }}">{{ row.state }}</span></td>
                            <td style="font-size: 12px; color: #6b7280;">{{ row.date }}</td>
                            <td><a href="{{ row.author_url }}" class="author-tag" target="_blank">{{ row.author }}</a></td>
                            <td style="font-size: 14px; max-width: 350px;">{{ row.title }}</td>
                            <td>
                                {% if row.session_url != 'N/A' %}
                                    <a href="{{ row.session_url }}" class="btn" target="_blank">View Session</a>
                                {% else %}
                                    <span style="color: #9ca3af; font-size: 12px;">No Link</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

                {% if comments_data %}
                <h2>Comments from First PR (#{{ first_pr_number }})</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Author</th>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Comment</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for comment in comments_data %}
                        <tr>
                            <td><a href="{{ comment.author_url }}" class="author-tag" target="_blank">{{ comment.author }}</a></td>
                            <td style="font-size: 12px; color: #6b7280;">{{ comment.date }}</td>
                            <td style="font-size: 11px; font-weight: 600; color: #7c3aed;">{% if comment.is_pr_body %}PR Body{% else %}Comment{% endif %}</td>
                            <td><div class="comment-body">{{ comment.body }}</div></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% elif first_pr_number and not comments_error %}
                <h2>Comments from First PR (#{{ first_pr_number }})</h2>
                <p style="color: #6b7280; font-size: 14px;">No comments found on this PR.</p>
                {% elif comments_error %}
                <h2>Comments from First PR (#{{ first_pr_number }})</h2>
                <p style="color: #dc2626; font-size: 14px;"><strong>Error:</strong> {{ comments_error }}</p>
                {% endif %}
            </div>
        </body>
        </html>
    """, repo=REPO, rows=rows, first_pr_number=first_pr_number, comments_data=comments_data, comments_error=comments_error)

if __name__ == "__main__":
    # debug=True allows the server to reload when you make changes
    app.run(host="127.0.0.1", port=5000, debug=True)