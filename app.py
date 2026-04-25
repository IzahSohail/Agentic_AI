# Import Flask to create the web app
from flask import Flask
import webbrowser
import threading

# Create the Flask app instance
app = Flask(__name__)

# Define the home route - this runs when you visit http://127.0.0.1:5000/
@app.route("/")
def home():
    # Return a simple HTML page that displays "Hello, World!"
    return "<h1>Hello, World!</h1>"

def open_browser():
    # Open the browser automatically after the server starts
    webbrowser.open("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Open the browser in a separate thread so the server can start first
    threading.Timer(1, open_browser).start()
    # Start the Flask development server
    # debug=True enables auto-reload and helpful error messages while learning
    app.run(host="127.0.0.1", port=5000, debug=True)