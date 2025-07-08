import os
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration
# GitHub repository information
REPO_URL = "https://github.com/marketcalls/autoinstall.git"
REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update_from_github():
    try:
        if not os.path.exists(REPO_PATH):
            # Clone the repository if it doesn't exist
            subprocess.check_output(f"git clone {REPO_URL} {REPO_PATH}", shell=True)
            result = "Repository successfully cloned."
        else:
            # Update the repository if it exists
            result = subprocess.check_output(f"cd {REPO_PATH} && git pull", shell=True)
            result = result.decode('utf-8')
        
        return jsonify({"status": "success", "message": result})
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode('utf-8') if e.output else str(e)
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
