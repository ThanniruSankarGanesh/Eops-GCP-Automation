from google.cloud import storage

def get_buckets(project_id):
    buckets = []
    client = storage.Client(project=project_id)
    for bucket in client.list_buckets():
        buckets.append({
            'name': bucket.name,
            'location': bucket.location,
            'storage_class': bucket.storage_class,
            'created': bucket.time_created.strftime('%Y-%m-%d')
        })
    return buckets
