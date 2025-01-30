# GoogleCreateProjects

This Python script automates the creation of Google Cloud Projects. It utilizes the Google Cloud Resource Manager API to create projects, handling project ID generation, naming, and optional billing account linking.

## Prerequisites

* **Python 3.6+**
* **Credentials file (`credentials.json`)**: You need to set up OAuth 2.0 credentials for your Google Cloud account.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/not-lucky/GoogleCreateProjects.git
   cd GoogleCreateProjects
   ```

2. **Install required Python libraries:**
   ```bash
   pip install -r requirements.txt
   ```

## Setup Credentials

1. **Create a Google Cloud Project** (if you don't have one already) in the [Google Cloud Console](https://console.cloud.google.com/).
2. **Enable the Cloud Resource Manager API** for your project.
3. **Create OAuth 2.0 credentials:**
    * Go to the [Credentials page](https://console.cloud.google.com/apis/credentials) in the Google Cloud Console.
    * Click **Create credentials** > **OAuth client ID**.
    * Select **Desktop app** as the Application type.
    * Enter a name (e.g., "Project Creator").
    * Click **Create**.
    * Download the credentials as **JSON** and save it as `credentials.json` in the same directory as the script.

## Usage

1. **Run the script:**
   ```bash
   python main.py  # Replace your_script_name.py with the actual script file name.
   ```

2. **Follow the prompts:**
   * The script will ask for:
     * The starting number for project numbering (e.g., 1).
     * The number of projects to create.
     * (Optional) Your Billing Account ID.
   * You will be prompted to authorize the script to access your Google Cloud account in your browser.

## Logging

The script logs detailed information to both the console and a file named `project_creation.log`. Check this file for details about project creation status and any errors.

---

**Note:** This script assumes you have the necessary permissions to create projects in your Google Cloud organization or project.  Ensure your Google Cloud account is properly configured before running the script.
