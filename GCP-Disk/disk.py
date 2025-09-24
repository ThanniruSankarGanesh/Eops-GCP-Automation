import os
import csv
from datetime import datetime
from google.cloud import compute_v1
from google.cloud import storage

# Define your GCP project IDs directly here
project_ids = [
    "eops-gcp-lab"
]

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")

def classify_disk_usage(users):
    if not users:
        return "Unattached"
    for user in users:
        if "instances" in user:
            return "Attached to VM"
    return "Used by Service"

def list_managed_disks():
    disks_client = compute_v1.DisksClient()
    rows = []

    for project_id in project_ids:
        print(f"🔍 Scanning project: {project_id}")
        aggregated_list = disks_client.aggregated_list(project=project_id)
        for zone, disks_scoped_list in aggregated_list:
            if disks_scoped_list and disks_scoped_list.disks:
                for disk in disks_scoped_list.disks:
                    try:
                        disk_name = disk.name
                        size_gb = disk.size_gb
                        disk_type = disk.type_.split('/')[-1] if disk.type_ else 'Unknown'
                        location = zone.split('zones/')[-1]
                        status = disk.status
                        creation_date = disk.creation_timestamp
                        used_by = disk.users[0].split('/')[-1] if disk.users else 'None'
                        usage_type = classify_disk_usage(disk.users)

                        row = [
                            project_id,
                            disk_name,
                            size_gb,
                            disk_type,
                            location,
                            status,
                            creation_date,
                            used_by,
                            usage_type
                        ]
                        rows.append(row)
                    except Exception as e:
                        print(f"⚠️ Error processing disk {disk.name}: {e}")
    return rows

if __name__ == "__main__":
    csv_filename = 'gcp_disk_inventory.csv'
    disks_data = list_managed_disks()

    # Write to CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Project", "Disk Name", "Size (GB)", "Disk Type", "Location",
            "Status", "Creation Date", "Used By", "Usage Type"
        ])
        writer.writerows(disks_data)

    # Upload to GCS
    upload_to_gcs(
        bucket_name='gcp_cloud_dashboard',
        source_file_name=csv_filename,
        destination_blob_name='reports/All_Disks.csv'
    )
