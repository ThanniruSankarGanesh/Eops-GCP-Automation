from google.cloud import compute_v1

def get_orphaned_disks(project_id):
    disks_client = compute_v1.DisksClient()
    zone_client = compute_v1.ZonesClient()
    orphaned_disks = []

    zones = [zone.name for zone in zone_client.list(project=project_id)]

    for zone in zones:
        request = compute_v1.ListDisksRequest(project=project_id, zone=zone)
        for disk in disks_client.list(request=request):
            if not disk.users:
                orphaned_disks.append({
                    'name': disk.name,
                    'zone': zone,
                    'size_gb': disk.size_gb,
                    'type': disk.type.split('/')[-1],
                    'status': disk.status,
                    'creation_timestamp': disk.creation_timestamp
                })

    return orphaned_disks
