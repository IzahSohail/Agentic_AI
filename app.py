# Import Flask to create the web application
from flask import Flask

# Create the Flask app instance
app = Flask(__name__)

# Define the home route — visits to "/" will call this function
@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"

if __name__ == "__main__":
    # Run the app locally at http://127.0.0.1:5000
    # debug=True allows the server to reload when you make changes
    app.run(host="127.0.0.1", port=5000, debug=True)