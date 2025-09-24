from google.cloud import compute_v1

def get_snapshots(project_id):
    snapshot_client = compute_v1.SnapshotsClient()
    snapshots = []

    request = compute_v1.ListSnapshotsRequest(project=project_id)
    for snapshot in snapshot_client.list(request=request):
        snapshots.append({
            'name': snapshot.name,
            'status': snapshot.status,
            'size_gb': snapshot.disk_size_gb,
            'source_disk': snapshot.source_disk,
            'creation_time': snapshot.creation_timestamp,
            'location': snapshot.storage_locations[0] if snapshot.storage_locations else "global"
        })
    return snapshots