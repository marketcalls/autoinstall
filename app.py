import os
import subprocess
import hashlib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration
# GitHub repository information
REPO_URL = "https://github.com/marketcalls/autoinstall.git"
REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo")

@app.route('/')
def index():
    return render_template('index.html')

def get_file_hash(file_path):
    """Calculate the SHA-256 hash of a file."""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash

def install_requirements(req_file_path):
    """Install packages from requirements.txt"""
    try:
        result = subprocess.check_output(f"pip install -r {req_file_path}", shell=True)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Error installing requirements: {str(e)}"

@app.route('/update', methods=['POST'])
def update_from_github():
    try:
        messages = []
        req_updated = False
        req_file = os.path.join(REPO_PATH, 'requirements.txt')
        
        # Get hash of requirements.txt before update (if exists)
        old_hash = get_file_hash(req_file)
        
        if not os.path.exists(REPO_PATH):
            # Clone the repository if it doesn't exist
            clone_result = subprocess.check_output(f"git clone {REPO_URL} {REPO_PATH}", shell=True)
            messages.append(f"Repository successfully cloned: {clone_result.decode('utf-8').strip()}")
            
            # Install requirements if present after clone
            if os.path.exists(req_file):
                install_msg = install_requirements(req_file)
                messages.append(f"Initial requirements installed: {install_msg.strip()}")
                req_updated = True
        else:
            # Update the repository if it exists
            pull_result = subprocess.check_output(f"cd {REPO_PATH} && git pull", shell=True)
            pull_msg = pull_result.decode('utf-8').strip()
            messages.append(f"Repository updated: {pull_msg}")
            
            # Check if requirements.txt changed
            new_hash = get_file_hash(req_file)
            if new_hash and (old_hash != new_hash):
                install_msg = install_requirements(req_file)
                messages.append(f"Requirements updated: {install_msg.strip()}")
                req_updated = True
            elif not pull_msg.startswith("Already up to date."):
                messages.append("No changes detected in requirements.txt")
        
        result_message = "\n\n".join(messages)
        return jsonify({"status": "success", "message": result_message, "requirements_updated": req_updated})
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode('utf-8') if e.output else str(e)
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
