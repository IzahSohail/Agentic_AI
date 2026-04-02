# Copilot PR Dashboard

A Flask web app that fetches and displays all closed Pull Requests authored by GitHub Copilot in a given repository, using the GitHub Search API.

## What it does
- Queries the GitHub API for PRs authored by `@copilot` in a target repo
- Shows a table of PRs with status, author, date, title, and a link to the Copilot Workspace session
- Displays the body and comments of the most recent PR

## Project files
- `app.py` — Main Flask application
- `requirements.txt` — Python dependencies
- `.env.example` — Template for your environment variables

## Setup

1. Copy `.env.example` to `.env` and add your GitHub token:

   ```
   GITHUB_TOKEN=your_token_here
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

## Requirements
- Python 3.8+
- A GitHub personal access token with `repo` read access
