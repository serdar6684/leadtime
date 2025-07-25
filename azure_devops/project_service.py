from azure_devops.api_client import AzureDevOpsClient

def get_project_id(client: AzureDevOpsClient, project_name: str) -> str:
    endpoint = "/_apis/projects"
    params = {"api-version": client.api_version}
    data = client.get(endpoint, params=params)

    for project in data.get("value", []):
        if project.get("name") == project_name:
            return project.get("id")

    raise ValueError(f"Projet nommé '{project_name}' introuvable.")
