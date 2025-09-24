import os
import google.auth
from googleapiclient.discovery import build
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def generate_shared_vpc_report():
    def get_shared_vpc_details():
        credentials, project = google.auth.default()
        service = build('compute', 'v1', credentials=credentials)
        
        shared_vpc_data = []

        for project_id in project_ids:
            print(f"Checking project: {project_id}")
            request = service.projects().get(project=project_id)
            project_data = request.execute()

            if 'xpnProjectStatus' in project_data and project_data['xpnProjectStatus'] == 'HOST':
                essential_info = {
                    "Project ID": project_id,
                    "Name": project_data.get('name'),
                    "ID": project_data.get('id'),
                    "Creation Timestamp": project_data.get('creationTimestamp'),
                    "Project Status": project_data.get('xpnProjectStatus'),
                }
                shared_vpc_data.append(essential_info)
        
        return shared_vpc_data

    return get_shared_vpc_details()