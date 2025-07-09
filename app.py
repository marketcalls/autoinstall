import os
import subprocess
import hashlib
import requests
from packaging import version
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration
# GitHub repository information
REPO_URL = "https://github.com/marketcalls/autoinstall.git"
REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo")

@app.route('/')
def index():
    current_version = get_current_version()
    return render_template('index.html', current_version=current_version)

@app.route('/version', methods=['GET'])
def get_version_info():
    current_version = get_current_version()
    remote_version = get_remote_version()
    update_available = False
    
    if remote_version and compare_versions(current_version, remote_version):
        update_available = True
    
    return jsonify({
        "current_version": current_version,
        "remote_version": remote_version,
        "update_available": update_available
    })

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

def get_current_version():
    """Get the current version from version.txt"""
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.txt')
    try:
        with open(version_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"  # Default version

def get_remote_version():
    """Get the latest version from the remote repository"""
    try:
        # Check version.txt from the remote repo
        url = f"https://raw.githubusercontent.com/marketcalls/autoinstall/master/version.txt"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        return None
    except Exception as e:
        print(f"Error getting remote version: {e}")
        return None

def compare_versions(current, remote):
    """Compare current and remote versions"""
    try:
        return version.parse(remote) > version.parse(current)
    except Exception:
        return False

def update_local_version(new_version):
    """Update the local version file"""
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.txt')
    try:
        with open(version_file, 'w') as f:
            f.write(new_version)
        return True
    except Exception as e:
        print(f"Error updating version file: {e}")
        return False

@app.route('/update', methods=['POST'])
def update_from_github():
    try:
        messages = []
        req_updated = False
        version_updated = False
        req_file = os.path.join(REPO_PATH, 'requirements.txt')
        
        # Check current version
        current_version = get_current_version()
        messages.append(f"Current version: {current_version}")
        
        # Check for new version
        remote_version = get_remote_version()
        if remote_version:
            if compare_versions(current_version, remote_version):
                messages.append(f"🚀 New version available: {remote_version} (current: {current_version})")
                version_updated = True
            else:
                messages.append(f"✅ You have the latest version: {current_version}")
        else:
            messages.append("⚠️ Could not check remote version")
        
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
        
        # Update local version if newer version was found and pulled
        if version_updated and remote_version:
            if update_local_version(remote_version):
                messages.append(f"✅ Version updated to: {remote_version}")
            else:
                messages.append("⚠️ Failed to update local version file")
        
        result_message = "\n\n".join(messages)
        return jsonify({
            "status": "success", 
            "message": result_message, 
            "requirements_updated": req_updated,
            "version_updated": version_updated,
            "current_version": current_version,
            "remote_version": remote_version
        })
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode('utf-8') if e.output else str(e)
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
