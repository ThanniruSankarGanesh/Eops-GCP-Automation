from google.cloud import compute_v1

def get_snapshot_schedules(project_id):
    client = compute_v1.ResourcePoliciesClient()
    snapshot_schedules = []

    region_client = compute_v1.RegionsClient()
    regions = [region.name for region in region_client.list(project=project_id)]

    for region in regions:
        request = compute_v1.ListResourcePoliciesRequest(
            project=project_id,
            region=region
        )

        for policy in client.list(request=request):
            if policy.snapshot_schedule_policy:
                snapshot_schedules.append({
                    'name': policy.name,
                    'region': region,
                    'description': policy.description,
                    'creation_timestamp': policy.creation_timestamp,
                    'schedule': policy.snapshot_schedule_policy.schedule.__class__.__name__,
                    'retention_policy': policy.snapshot_schedule_policy.retention_policy.max_retention_days,
                    'labels': getattr(policy, 'labels', {})
                })

    return snapshot_schedules