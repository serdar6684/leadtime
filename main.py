from azure_devops.api_client import AzureDevOpsClient
from azure_devops.project_service import get_project_id
import config
from config import AZURE_ORG_URL, AZURE_RELEASE_URL, API_VERSION
from azure_devops.release_definition_service import get_release_definition_id

def main():
    client_core = AzureDevOpsClient(config.AZURE_ORG_URL, config.API_VERSION)
    client_release = AzureDevOpsClient(config.AZURE_RELEASE_URL, config.API_VERSION)

    try:
        project_id = get_project_id(client_core, config.PROJECT_NAME)
        print(f"Project ID pour 'One' : {project_id}")

        release_def_id = get_release_definition_id(
            client_release, project_id, config.STAGE_NAME
        )
        print(f"Release Definition ID : {release_def_id}")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
