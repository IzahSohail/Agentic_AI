# Copilot PR Dashboard

A Django web app that fetches and displays all closed Pull Requests authored by GitHub Copilot in a given repository, using the GitHub Search API.

## What it does
- Queries the GitHub API for PRs authored by `@copilot` in a target repo
- Shows a table of PRs with status, author, date, title, and a link to the Copilot Workspace session
- Displays the body and comments of the most recent PR

## Project files
- `app.py` — Entry point; starts the Django development server
- `manage.py` — Standard Django management utility
- `copilot_dashboard/` — Django project package (settings, URL routing, WSGI)
- `dashboard/` — Django app containing views, URL config, and HTML template
- `requirements.txt` — Python dependencies
- `.env.example` — Template for your environment variables

## Setup

1. Copy `.env.example` to `.env` and add your GitHub token:

   ```
   GITHUB_TOKEN=your_token_here
   ```

   Optionally, override the default target repository:

   ```
   GITHUB_REPO=owner/repo
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open your browser to: http://127.0.0.1:5000/

You can also use Django's standard management utility for other tasks:

```bash
python manage.py runserver        # same as python app.py
python manage.py check            # verify configuration
```

## Requirements
- Python 3.8+
- A GitHub personal access token with `repo` read access

---

## API Documentation

This app communicates with the **GitHub REST API v3**. All requests require authentication via a personal access token.

### Authentication

Every request includes the following HTTP header:

```
Authorization: Bearer <GITHUB_TOKEN>
Accept: application/vnd.github+json
```

The token is loaded from the `GITHUB_TOKEN` environment variable in your `.env` file.

---

### 1. Search Pull Requests

Retrieves all closed Pull Requests authored by GitHub Copilot in the configured repository.

**Endpoint**
```
GET https://api.github.com/search/issues
```

**Query Parameters**

| Parameter  | Type    | Description                                      |
|------------|---------|--------------------------------------------------|
| `q`        | string  | Search query. Example: `repo:owner/repo is:pr is:closed author:@copilot` |
| `per_page` | integer | Number of results per page (max 100). Default: `100` |
| `page`     | integer | Page number for pagination. Default: `1`         |

**Example Request**
```
GET https://api.github.com/search/issues?q=repo:owner/repo+is:pr+is:closed+author:@copilot&per_page=100&page=1
```

**Example Response (200 OK)**
```json
{
  "total_count": 2,
  "incomplete_results": false,
  "items": [
    {
      "number": 42,
      "title": "Fix: Update readme",
      "state": "closed",
      "created_at": "2024-01-15T10:00:00Z",
      "html_url": "https://github.com/owner/repo/pull/42",
      "body": "Session: https://copilot-workspace.githubnext.com/...",
      "user": {
        "login": "copilot",
        "html_url": "https://github.com/copilot"
      }
    }
  ]
}
```

**Error Responses**

| Status | Meaning                                      |
|--------|----------------------------------------------|
| `401`  | Invalid or missing authentication token      |
| `403`  | Rate limit exceeded or insufficient scope    |
| `422`  | Validation failed — malformed search query   |

---

### 2. List PR Comments

Fetches all comments for a specific pull request (identified by its PR number).

**Endpoint**
```
GET https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments
```

**Path Parameters**

| Parameter      | Type    | Description                              |
|----------------|---------|------------------------------------------|
| `owner`        | string  | GitHub username or organization name     |
| `repo`         | string  | Repository name                          |
| `issue_number` | integer | The pull request / issue number          |

**Query Parameters**

| Parameter  | Type    | Description                                        |
|------------|---------|----------------------------------------------------|
| `per_page` | integer | Number of results per page (max 100). Default: `100` |
| `page`     | integer | Page number for pagination. Default: `1`           |

**Example Request**
```
GET https://api.github.com/repos/owner/repo/issues/42/comments?per_page=100&page=1
```

**Example Response (200 OK)**
```json
[
  {
    "id": 1234567,
    "created_at": "2024-01-16T08:30:00Z",
    "html_url": "https://github.com/owner/repo/pull/42#issuecomment-1234567",
    "body": "Looks good to me!",
    "user": {
      "login": "reviewer",
      "html_url": "https://github.com/reviewer"
    }
  }
]
```

**Error Responses**

| Status | Meaning                                   |
|--------|-------------------------------------------|
| `401`  | Invalid or missing authentication token   |
| `404`  | Repository or PR not found                |

---

### Rate Limiting

GitHub's REST API allows **5,000 authenticated requests per hour**. The app uses paginated requests (100 results per page) to stay within limits. If you hit the rate limit, the API returns a `403` response.
