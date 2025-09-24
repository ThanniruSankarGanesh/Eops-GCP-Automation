import os
import json
from config import project_ids
from datetime import datetime, timezone

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
 
def get_snapshot_age(creation_time):
   # Calculate the age of the snapshot in days.
    creation_dt = datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    now = datetime.now(timezone.utc)
    age_days = (now - creation_dt).days
    return age_days

def generate_snapshot_report():
    def get_snapshots(project):
        try:
            command = f'gcloud compute snapshots list --format=json --project={project}'
            result = os.popen(command).read()
            snapshots = json.loads(result)
            return snapshots
        except Exception as e:
            print(f"Error fetching snapshots for project {project}: {e}")
            return []
 
    snapshot_data = []
    for project in project_ids:
        snapshots = get_snapshots(project)
        for snapshot in snapshots:
            creation_time = snapshot.get('creationTimestamp', 'N/A')
            age_days = get_snapshot_age(creation_time) if creation_time != 'N/A' else 'N/A'
            source_disk = snapshot.get('sourceDisk', 'N/A').split('/')[-1] if snapshot.get('sourceDisk') else 'N/A'
            location = snapshot.get('storageLocations', ['N/A'])[0] if snapshot.get('storageLocations') else 'N/A'
            creation_type = 'Auto' if snapshot.get('autoCreated', False) else 'Manual'          

            snapshot_data.append({
                "Project ID": project,
                "Name": snapshot.get('name', 'N/A'),
                "Status": snapshot.get('status', 'N/A'),
                "Size (GB)": snapshot.get('diskSizeGb', 'N/A'),
                "Creation Date": snapshot.get('creationTimestamp', 'N/A'),
                "Source Disk": source_disk,
                "Age (days)": age_days,
                "Creation Type": creation_type
            })
 
    return snapshot_data