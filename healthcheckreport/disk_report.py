import os
import json
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
 
def generate_disk_report():
    def get_disks(project):
        try:
            command = f'gcloud compute disks list --format=json --project={project}'
            result = os.popen(command).read()
            disks = json.loads(result)
            return disks
        except Exception as e:
            print(f"Error retrieving disks for project {project}: {e}")
            return []
 
    disk_data = []
    for project in project_ids:
        disks = get_disks(project)
        for disk in disks:
            disk_type = disk.get('type', '').split('/')[-1]
            users = ', '.join([user.split('/')[-1] for user in disk.get('users', [])])           
            zone_full = disk.get('zone', '')
            zone = zone_full.split('/')[-1] if zone_full else 'N/A'
            
            disk_data.append({
                "Project ID": project,
                "Name": disk.get('name', 'N/A'),
                "Size (GB)": disk.get('sizeGb', 'N/A'),
                "Creation Date": disk.get('creationTimestamp', 'N/A'),
                "Status": disk.get('status', 'N/A'),
                "Type": disk_type,
                "Zone": zone,
                "Users": users,
                "Description": disk.get('description', 'N/A')
            })
 
    return disk_data