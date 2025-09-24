from google.cloud import compute_v1
from google.cloud import bigquery
from datetime import datetime

def get_instances(project_id):
    instances = []
    instance_client = compute_v1.InstancesClient()
    agg_list = instance_client.aggregated_list(project=project_id)

    for zone, response in agg_list:
        if response.instances:
            for instance in response.instances:
                instances.append({
                    'name': instance.name,
                    'zone': zone.split('/')[-1],
                    'status': instance.status,
                    'machine_type': instance.machine_type.split('/')[-1]
                })

    upload_vm_data_to_bigquery(instances, project_id)

    return instances

def upload_vm_data_to_bigquery(vm_data, project_id):
    client = bigquery.Client()
    table_id = "gcp_resource_dashboard.vm_inventory"

    rows_to_insert = []
    for vm in vm_data:
        rows_to_insert.append({
            "project_id": project_id,
            "name": vm["name"],
            "zone": vm["zone"],
            "status": vm["status"],
            "machine_type": vm["machine_type"],
            "timestamp": datetime.utcnow().isoformat()
        })

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print("Failed to insert rows into BigQuery:", errors)
    else:
        print(f"Uploaded {len(rows_to_insert)} VM(s) from project '{project_id}' to BigQuery.")