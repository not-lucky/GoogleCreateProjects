import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import re
import secrets
import string
from google_auth_oauthlib.flow import InstalledAppFlow

# --- Logging Configuration ---
LOG_FILE = "project_creation.log"  # Name of the log file
LOG_LEVEL = logging.INFO

# Configure logging to write to both console and file
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to file
        logging.StreamHandler(),  # Log to console
    ],
)


def create_google_project(
    project_id, project_name=None, billing_account_id=None, credentials=None
):
    """
    Creates a new Google Cloud Project.

    This function uses the Google Cloud Resource Manager API to create a new project.
    It handles project ID validation, project naming, billing account association,
    and uses OAuth 2.0 credentials for authentication. It also includes error handling
    and waits for the project creation operation to complete.
    Logs detailed information about the project creation process to both console and a log file.

    Args:
        project_id (str): The desired unique ID for the new project.
                           Constraints: 6-30 lowercase letters, digits, or hyphens;
                           starts with a letter, ends with letter or digit.
        project_name (str, optional):  A user-friendly display name for the project.
                                     Defaults to `project_id` if not provided.
        billing_account_id (str, optional): The ID of the billing account to link to this project.
                                             If None, the project will be linked to the default
                                             billing account associated with the credentials (if any).
        credentials (google.oauth2.credentials.Credentials): OAuth 2.0 credentials object
                                                             obtained using `InstalledAppFlow` or similar.
                                                             This is required for authenticating with Google Cloud APIs.

    Returns:
        dict or None:  Returns a dictionary representing the created project resource if successful.
                       The dictionary contains project details as returned by the Google Cloud API.
                       Returns None if project creation fails due to errors like invalid credentials,
                       API errors, or project ID conflicts. Error details are logged.
    """
    # Check if OAuth 2.0 credentials are provided.
    if credentials is None:
        logging.error("OAuth 2.0 Credentials object is required to create a project.")
        return None

    try:
        # Build the Cloud Resource Manager service client using provided credentials.
        # This client is used to interact with the Google Cloud Resource Manager API.
        service = build("cloudresourcemanager", "v1", credentials=credentials)

        # Construct the request body for creating a new project.
        # Includes project ID and project name.
        project_body = {
            "project_id": project_id,
            "name": project_name
            if project_name
            else project_id,  # Use project_id as project name if project_name is not provided.
        }
        # If a billing account ID is provided, add billing account information to the project body.
        if billing_account_id:
            project_body["parent"] = {
                "type": "billingAccounts",
                "id": billing_account_id,
            }

        # Initiate the project creation request to the Google Cloud API.
        request = service.projects().create(body=project_body)
        operation = request.execute()

        logging.info(f"Project creation operation started for project ID: {project_id}")

        # Poll the operation status until project creation is complete (success or failure).
        while True:
            operation_result = (
                service.operations().get(name=operation["name"]).execute()
            )

            if "done" in operation_result:
                if "error" in operation_result:
                    error = operation_result["error"]
                    logging.error(f"Error creating project {project_id}:")
                    logging.error(f"  Code: {error['code']}")
                    logging.error(f"  Message: {error['message']}")

                    if "details" in error:
                        logging.error("  Details:")
                        for detail in error["details"]:
                            logging.error(f"    - {detail}")

                    # Provide a specific solution for Terms of Service error, a common issue.
                    if "Terms of Service" in error["message"]:
                        logging.warning(
                            "\n\nSOLUTION FOR ERROR:\n\nGo to https://console.cloud.google.com/ of that "
                            + "google account, and open cloud shell (top right) or press 'gs', then Click 'Accept'. "
                            + "And try again."
                        )
                    return None
                else:
                    logging.info(f"Project {project_id} created successfully!")
                    project_resource = operation_result["response"]
                    return project_resource
                break
            else:
                logging.info("Waiting for project creation to complete...")
                time.sleep(
                    5
                )  # Wait for 5 seconds before checking operation status again.

    except HttpError as error:
        logging.error(f"An HTTP error occurred during project creation: {error}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during project creation: {e}")
        return None


def is_valid_project_id(project_id):
    """
    Validates if a given project ID string conforms to the Google Cloud Project ID requirements.

    Project IDs must be globally unique and follow specific naming conventions:
    - Length: 6 to 30 characters
    - Allowed characters: lowercase letters, digits, and hyphens
    - Must start with a lowercase letter
    - Must end with a lowercase letter or digit

    Args:
        project_id (str): The project ID string to validate.

    Returns:
        bool: True if the project_id is valid, False otherwise.
    """
    # Regular expression pattern to match valid project IDs.
    # ^[a-z]        : Must start with a lowercase letter.
    # [a-z0-9-]{4,28} : Followed by 4 to 28 lowercase letters, digits, or hyphens.
    # [a-z0-9]$     : Must end with a lowercase letter or digit.
    pattern = r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"
    return bool(
        re.match(pattern, project_id)
    )  # Returns True if pattern matches, False otherwise.


def generate_random_project_id(prefix="projectuwu-"):
    """
    Generates a random, valid Google Cloud Project ID.

    This function creates a project ID by combining a user-provided prefix with a randomly
    generated suffix. It ensures the generated ID conforms to the valid project ID format
    by validating it using the `is_valid_project_id` function.

    Args:
        prefix (str, optional):  The prefix to be used for the project ID.
                                 It's recommended to use a meaningful prefix to easily identify projects.
                                 Defaults to "projectuwu-".

    Returns:
        str: A randomly generated, valid project ID string.
    """
    while True:
        # Generate a random suffix of 15 lowercase letters and digits.
        random_suffix = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(15)
        )
        # Combine prefix and random suffix to create a potential project ID.
        project_id = f"{prefix}{random_suffix}"
        # Validate the generated project ID to ensure it meets the requirements.
        if is_valid_project_id(project_id):
            return project_id  # Return the valid project ID if it passes validation.
        else:
            logging.warning(
                f"Generated project ID '{project_id}' is not valid. Retrying..."
            )  # Log a warning if generated ID is invalid.


if __name__ == "__main__":
    # --- Configuration Section ---
    # Get the starting project number from the user.
    while True:
        try:
            start_number = int(
                input(
                    "Enter the initial number to start project numbering from (e.g., 1): "
                )
            )
            if start_number < 1 and start_number > 12:
                print(
                    "Please enter a number greater than or equal to 1 and less than 13."
                )
                continue
            break
        except ValueError:
            print(
                "Invalid input. Please enter an integer."
            )  # Handle non-integer input.

    # Get the number of projects to create from the user.
    while True:
        try:
            num_projects = int(input("Enter the number of projects to create: "))
            if num_projects < 1 and num_projects > 12:
                print(
                    "Please enter a number greater than or equal to 1 and less than 13."
                )
                continue
            break
        except ValueError:
            print(
                "Invalid input. Please enter an integer."
            )  # Handle non-integer input.

    # Get the Billing Account ID from the user (optional).
    BILLING_ACCOUNT_ID = (
        input("Enter your Billing Account ID (optional, leave blank to use default): ")
        or None
    )  # If blank input, set to None to use the default billing account.

    # Define the client secrets file and the required API scope.
    CLIENT_SECRETS_FILE = (
        "credentials.json"  # Path to your OAuth 2.0 Client IDs JSON file.
    )
    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform"
    ]  # Scope for Cloud Resource Manager API access.

    # --- OAuth 2.0 Authentication Flow ---
    # Initialize the OAuth 2.0 flow from client secrets file and requested scopes.
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    # Run the local server flow to obtain OAuth 2.0 credentials.
    # Opens a browser window for user authorization.
    credentials = flow.run_local_server(
        port=0
    )  # port=0 lets the system pick an open port.

    # --- Project Creation Summary Display ---
    logging.info("\n--- Project Creation Summary ---")
    logging.info(f"Starting Project Number: {start_number}")
    logging.info(f"Number of Projects to Create: {num_projects}")
    logging.info("Project IDs: Randomly generated.")
    logging.info("Project Names: Project1, Project2, etc.")
    logging.info(
        f"Authentication: Using OAuth 2.0 Client IDs from '{CLIENT_SECRETS_FILE}'"
    )
    if BILLING_ACCOUNT_ID:
        logging.info(f"Billing Account ID: {BILLING_ACCOUNT_ID}")
    else:
        logging.info("Billing Account: Default will be used if available.")
    logging.info("-----------------------------------\n")

    created_projects_info = []  # List to store information about successfully created projects.

    # --- Project Creation Loop ---
    for i in range(num_projects):
        project_number = start_number + i  # Calculate project number.
        project_name = f"project{project_number:02d}"  # Generate project name based on number (e.g., project01).
        project_id = generate_random_project_id(
            project_name + "-"
        )  # Generate a random project ID with project name as prefix.

        logging.info(f"\n--- Creating Project {project_number} ---")
        logging.info(f"  Project Name: {project_name}")
        logging.info(f"  Project ID:   {project_id}")

        # Create the Google Cloud Project using the create_google_project function.
        new_project = create_google_project(
            project_id, project_name, BILLING_ACCOUNT_ID, credentials=credentials
        )

        if new_project:
            created_projects_info.append(
                new_project
            )  # Add project info to the list if creation was successful.
        else:
            logging.error(
                f"Project '{project_id}' creation failed. See error messages above."
            )

    # --- Final Project Creation Summary ---
    logging.info("\n--- Project Creation Summary ---")
    if created_projects_info:
        logging.info("Successfully created projects:")
        # Log details of each successfully created project.
        for project in created_projects_info:
            logging.info(
                f"  - Name: {project['name']}, ID: {project['projectId']}, Number: {project['projectNumber']}"
            )
    else:
        logging.info("No projects were successfully created.")
    logging.info("-----------------------------------\n")
