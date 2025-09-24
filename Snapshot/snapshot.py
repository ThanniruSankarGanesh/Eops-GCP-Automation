import os
import csv
from datetime import datetime
from google.cloud import compute_v1
from google.cloud import storage

# Load credentials from environment variable
json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")

def list_snapshots(project_id):
    snapshot_client = compute_v1.SnapshotsClient()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = 'gcp_snapshot_inventory.csv'
    html_filename = f'gcp_snapshot_inventory_{timestamp}.html'

    rows = []

    # Write CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Billing Account", "Project", "Snapshot Name", "Source Disk", "Size (MB)",
            "Creation Date", "Location", "Status"
        ])

        print(f"🔍 Processing project: {project_id}")
        snapshots = snapshot_client.list(project=project_id)
        for snapshot in snapshots:
            try:
                size_mb = round(snapshot.storage_bytes / (1024 ** 2), 2) if snapshot.storage_bytes else 0
                row = [
                    "Ergo",
                    project_id,
                    snapshot.name,
                    snapshot.source_disk.split('/')[-1] if snapshot.source_disk else 'Unknown',
                    size_mb,
                    snapshot.creation_timestamp.split('T')[0],
                    snapshot.storage_locations[0] if snapshot.storage_locations else 'Unknown',
                    snapshot.status
                ]
                rows.append(row)
                writer.writerow(row)
            except Exception as e:
                print(f"⚠️ Error processing snapshot {snapshot.name}: {e}")


    # Upload CSV to GCS
    upload_to_gcs(
        bucket_name='gcp_cloud_dashboard',
        source_file_name=csv_filename,
        destination_blob_name='reports/Snapshot.csv'
    )

if __name__ == "__main__":
    project_id = "eops-gcp-lab"
    list_snapshots(project_id)
