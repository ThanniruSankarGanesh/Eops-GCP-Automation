import os
import csv
from datetime import datetime
from google.cloud import storage

# Load credentials from environment variable
json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")

def list_buckets(project_ids):
    storage_client = storage.Client()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = 'gcp_bucket_inventory.csv'
    html_filename = f'gcp_bucket_inventory_{timestamp}.html'

    rows = []

    # Write CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Billing Account", "Project", "Bucket Name", "Location", "Storage Class",
            "Created Date", "Object Count", "Total Size (Bytes)"
        ])

        for project_id in project_ids:
            print(f"🔍 Processing project: {project_id}")
            buckets = storage_client.list_buckets(project=project_id)
            for bucket in buckets:
                try:
                    object_count = 0
                    total_size_bytes = 0

                    for blob in storage_client.list_blobs(bucket.name, versions=False):
                        object_count += 1
                        total_size_bytes += blob.size

                    row = [
                        "Ergo",
                        project_id,
                        bucket.name,
                        bucket.location,
                        bucket.storage_class,
                        bucket.time_created.strftime('%Y-%m-%d'),
                        object_count,
                        total_size_bytes
                    ]
                    writer.writerow(row)
                    rows.append(row)
                except Exception as e:
                    print(f"⚠️ Error processing bucket {bucket.name}: {e}")


    # Upload CSV to GCS
    upload_to_gcs(
        bucket_name='gcp_cloud_dashboard',
        source_file_name=csv_filename,
        destination_blob_name='reports/Bucket.csv'
    )

if __name__ == "__main__":
    project_ids = ["eops-gcp-lab"]
    list_buckets(project_ids)
