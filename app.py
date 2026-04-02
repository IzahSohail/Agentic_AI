"""
Entry point for the Copilot PR Dashboard Django application.
Run the development server with: python app.py
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "copilot_dashboard.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed? "
            "Run: pip install -r requirements.txt"
        ) from exc
    # Start the development server on the same host/port as before
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:5000"])


if __name__ == "__main__":
    main()