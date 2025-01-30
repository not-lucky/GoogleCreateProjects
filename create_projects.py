from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import re
import secrets
import string
from google_auth_oauthlib.flow import InstalledAppFlow  # For OAuth 2.0 flow


def create_google_project(
    project_id, project_name=None, billing_account_id=None, credentials=None
):
    """Creates a new Google Cloud project using provided OAuth 2.0 credentials.

    Args:
        project_id (str): The unique, user-assigned ID of the project.
                            It must be 6 to 30 lowercase letters, digits, or hyphens.
                            It must start with a letter, end with a letter or digit,
                            and contain only lowercase letters, digits, or hyphens.
        project_name (str, optional): The display name of the project. Defaults to None.
        billing_account_id (str, optional): The ID of the billing account to associate
                                            with the project. If None, the default
                                            billing account associated with your
                                            credentials will be used (if any).
        credentials (google.oauth2.credentials.Credentials): OAuth 2.0 Credentials object.
                                                             This should be obtained using InstalledAppFlow or similar.

    Returns:
        dict: The created project resource if successful, None otherwise.
              Returns None if there's an error during project creation.
    """

    if credentials is None:
        print("Error: OAuth 2.0 Credentials object is required.")
        return None

    try:
        # Create a Resource Manager service client using the provided credentials.
        service = build("cloudresourcemanager", "v1", credentials=credentials)

        project_body = {
            "project_id": project_id,
            "name": project_name
            if project_name
            else project_id,  # Use project_id as name if name is not provided
        }
        if billing_account_id:
            project_body["parent"] = {
                "type": "billingAccounts",
                "id": billing_account_id,
            }

        # Create the project
        request = service.projects().create(body=project_body)
        operation = request.execute()

        print(f"Project creation operation started for project ID: {project_id}")

        # Wait for the operation to complete (project creation can take time)
        while True:
            operation_result = (
                service.operations().get(name=operation["name"]).execute()
            )
            if "done" in operation_result:
                if "error" in operation_result:
                    error = operation_result["error"]
                    print(f"Error creating project {project_id}:")
                    print(f"  Code: {error['code']}")
                    print(f"  Message: {error['message']}")
                    if "details" in error:
                        print("  Details:")
                        for detail in error["details"]:
                            print(f"    - {detail}")

                    if "Terms of Service" in error["message"]:
                        print(
                            "\n\nSOLUTION FOR ERROR:\n\nGo to https://console.cloud.google.com/ of that "
                            + "google account, and open cloud shell (top right) or press 'gs', then Click 'Accept'. "
                            + "And try again."
                        )
                    return None  # Project creation failed
                else:
                    print(f"Project {project_id} created successfully!")
                    project_resource = operation_result[
                        "response"
                    ]  # The project resource is in the response
                    return project_resource  # Project creation successful
                break
            else:
                print("Waiting for project creation to complete...")
                time.sleep(5)  # Wait for 5 seconds before checking again

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def is_valid_project_id(project_id):
    """Validates if a project ID conforms to the required format."""
    pattern = (
        r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"  # Relaxed to 4-28 for practical project ids
    )
    return bool(re.match(pattern, project_id))


def generate_random_project_id(prefix="projectuwu-"):
    """Generates a random, valid project ID."""
    while True:
        random_suffix = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(15)
        )  # 15 random chars
        project_id = f"{prefix}{random_suffix}"
        if is_valid_project_id(project_id):  # Basic validation
            return project_id
        else:
            print(
                f"Generated project ID '{project_id}' is not valid. Retrying..."
            )  # For debugging if needed


if __name__ == "__main__":
    # --- Configuration ---
    while True:
        try:
            start_number = int(
                input(
                    "Enter the initial number to start project numbering from (e.g., 1): "
                )
            )
            if start_number < 1:
                print("Please enter a number greater than or equal to 1.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    while True:
        try:
            num_projects = int(input("Enter the number of projects to create: "))
            if num_projects < 1:
                print("Please enter a number greater than or equal to 1.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    BILLING_ACCOUNT_ID = (
        input("Enter your Billing Account ID (optional, leave blank to use default): ")
        or None
    )

    CLIENT_SECRETS_FILE = "credentials.json"  # Assuming your OAuth 2.0 Client IDs file is named 'credentials.json' and in the same directory.
    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform"
    ]  # Scope needed for Cloud Resource Manager API

    # --- OAuth 2.0 Flow ---
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(
        port=0
    )  # Opens a browser window for authorization

    print("\n--- Project Creation Summary ---")
    print(f"Starting Project Number: {start_number}")
    print(f"Number of Projects to Create: {num_projects}")
    print("Project IDs: Randomly generated.")
    print("Project Names: Project1, Project2, etc.")  # Names are fixed now
    print(f"Authentication: Using OAuth 2.0 Client IDs from '{CLIENT_SECRETS_FILE}'")
    if BILLING_ACCOUNT_ID:
        print(f"Billing Account ID: {BILLING_ACCOUNT_ID}")
    else:
        print("Billing Account: Default will be used if available.")
    print("-----------------------------------\n")

    created_projects_info = []

    for i in range(num_projects):
        project_number = start_number + i
        project_name = f"project{project_number:02d}"  # Names are fixed now, modified to reflect double digit
        project_id = generate_random_project_id(
            project_name + "-"
        )  # Generate random project ID

        print(f"\n--- Creating Project {project_number} ---")
        print(f"  Project Name: {project_name}")
        print(f"  Project ID:   {project_id}")

        new_project = create_google_project(
            project_id, project_name, BILLING_ACCOUNT_ID, credentials=credentials
        )  # Pass OAuth credentials

        if new_project:
            created_projects_info.append(new_project)
        else:
            print(f"Project '{project_id}' creation failed. See error messages above.")

    print("\n--- Project Creation Summary ---")
    if created_projects_info:
        print("Successfully created projects:")
        for project in created_projects_info:
            print(
                f"  - Name: {project['name']}, ID: {project['projectId']}, Number: {project['projectNumber']}"
            )
    else:
        print("No projects were successfully created.")
    print("-----------------------------------\n")
