"""
Simple Flask app that starts a local web server,
opens a browser tab, and shows "Hello, World!".
"""

from flask import Flask
import threading
import webbrowser

# Create the Flask app instance.
app = Flask(__name__)


@app.route("/")
def hello_world():
    """Return a simple greeting when users visit the home page."""
    return "Hello, World!"


def open_browser() -> None:
    """Open the default browser to the app URL."""
    webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    # Start a short timer so the browser opens right after the server starts.
    threading.Timer(1.0, open_browser).start()

    # Run the local development server.
    # use_reloader=False prevents opening multiple browser tabs.
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
