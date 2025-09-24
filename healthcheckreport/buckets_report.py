import os
from google.cloud import storage
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
 
def generate_buckets_report():
    def format_labels(labels):
        return ', '.join([f"{key}: {value}" for key, value in labels.items()])
 
    def list_buckets_info(project_id):
        client = storage.Client(project=project_id)
        buckets = client.list_buckets()
 
        buckets_data = []
 
        for bucket in buckets:
            soft_delete_policy = bucket._properties.get('softDeletePolicy', {})
            effective_time = soft_delete_policy.get('effectiveTime', None)
            retention_seconds = soft_delete_policy.get('retentionDurationSeconds', None)
 
            # Convert retention period from seconds to days
            retention_days = int(retention_seconds) // 86400 if retention_seconds else 'N/A'
 
            bucket_name = bucket.name
            location = bucket.location
            location_type = bucket.location_type
            storage_class = bucket.storage_class
            created_time = bucket.time_created
            updated_time = bucket.updated
            versioning_enabled = bucket.versioning_enabled
            labels = format_labels(bucket.labels or {})
            uniform_bucket_level_access = "Uniform" if bucket.iam_configuration.uniform_bucket_level_access_enabled else "Fine-grained"
 
            buckets_data.append({
                "Project ID": project_id,
                "Bucket Name": bucket_name,
                "Location": location,
                "Location Type": location_type,
                "Storage Class": storage_class,
                "Created Time": created_time,
                "Last Updated Time": updated_time,
                "Versioning Enabled": versioning_enabled,
                "Labels": labels,
                "Soft Deleted Policy Effective Date": effective_time if effective_time else 'N/A',
                "Retention Period (days)": retention_days,
                "Access Control": uniform_bucket_level_access
            })
 
        return buckets_data
 
    # Aggregate data for all projects
    all_buckets_data = []
    for project_id in project_ids:
        all_buckets_data.extend(list_buckets_info(project_id))
 
    return all_buckets_data