# GitHub Auto Update Flask Application

A simple Flask web application with a button to automatically update code from GitHub.

## Features

- One-click GitHub repository update/clone
- Automatic version checking and upgrade
- Automatic dependency installation from requirements.txt
- Visual feedback on update status with version notifications
- Simple and clean UI with version display

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure the repository:
   Edit the `app.py` file and update the `REPO_URL` variable with your GitHub repository URL.

3. Run the application:
   ```
   python app.py
   ```

4. Access the application in your browser at:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

Simply click the "Update from GitHub" button on the web page. The application will:
- Clone the repository if it doesn't exist locally
- Pull the latest changes if the repository exists

The status and results of the operation will be displayed on the page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
