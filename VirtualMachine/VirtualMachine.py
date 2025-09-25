import os
import csv
from datetime import datetime
from google.cloud import compute_v1
from google.cloud import storage

# Load credentials from environment variable
json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def get_machine_type_details(machine_type_url):
    machine_type_client = compute_v1.MachineTypesClient()
    machine_type = machine_type_url.split('/')[-1]
    zone = machine_type_url.split('/')[-3]
    project = machine_type_url.split('/')[-5]
    machine_type_details = machine_type_client.get(project=project, zone=zone, machine_type=machine_type)
    return machine_type_details.memory_mb

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")

def list_instances(project_ids):
    instance_client = compute_v1.InstancesClient()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = 'gcp_vm_inventory.csv'
    html_filename = f'gcp_vm_inventory_{timestamp}.html'

    rows = []

    # Write CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Billing Account", "Projects", "Instance Name", "Status", "Machine Type",
            "Memory (GB)", "OS Type", "OS Disk Name", "OS Disk Size (GB)", "Location", "Private IP", "External IP"
        ])

        for project_id in project_ids:
            print(f"🔍 Processing project: {project_id}")
            aggregated_list = instance_client.aggregated_list(project=project_id)
            for zone, instances_scoped_list in aggregated_list:
                if instances_scoped_list and instances_scoped_list.instances:
                    for instance in instances_scoped_list.instances:
                        try:
                            internal_ip = instance.network_interfaces[0].network_i_p
                            external_ip = (
                                instance.network_interfaces[0].access_configs[0].nat_i_p
                                if instance.network_interfaces[0].access_configs else 'No External IP'
                            )
                            os_disk = instance.disks[0] if instance.disks else None
                            machine_type = instance.machine_type
                            os_type = (
                                instance.disks[0].licenses[0].split('/')[-1]
                                if instance.disks and instance.disks[0].licenses else 'Unknown'
                            )
                            memory_mb = get_machine_type_details(machine_type)
                            memory_gb = round(memory_mb / 1024, 2)
                            location = zone.split('zones/')[-1]

                            row = [
                                "Ergo",
                                project_id,
                                instance.name,
                                instance.status,
                                machine_type.split('/')[-1],
                                memory_gb,
                                os_type,
                                os_disk.device_name if os_disk else 'No Disk',
                                os_disk.disk_size_gb if os_disk else 'No Disk',
                                location,
                                internal_ip,
                                external_ip
                            ]
                            writer.writerow(row)
                            rows.append(row)
                        except Exception as e:
                            print(f"⚠️ Error processing instance {instance.name}: {e}")

    # Upload CSV to GCS
    upload_to_gcs(
        bucket_name='gcp_cloud_dashboard',
        source_file_name=csv_filename,
        destination_blob_name='reports/VM.csv'
    )

if __name__ == "__main__":
    project_ids = ["eops-gcp-lab"]
    list_instances(project_ids)



