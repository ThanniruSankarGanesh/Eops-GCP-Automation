import os
from datetime import datetime
import concurrent.futures
import json
from config import project_ids, BUCKET_NAME
from scripts.compute import virtual_machines, snapshot_inventory, orphaned_disks, snapshot_schedule_report
from scripts.storage import bucket_inventory
from scripts.monitoring import metrics_utilization
from utils.html_generator import generate_html, render_project_section
from google.cloud import storage
from jinja2 import Environment, FileSystemLoader


def upload_to_gcs(bucket_name, source_file, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)
    print(f"Uploaded to GCS: gs://{bucket_name}/{destination_blob_name}")


def upload_json_to_gcs(bucket_name, data, project_id):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"raw_data/{project_id}.json")
    blob.upload_from_string(data=json.dumps(data, indent=2), content_type='application/json')
    print(f"Uploaded JSON: gs://{bucket_name}/raw_data/{project_id}.json")


def process_project(project_id):
    print(f"Processing project: {project_id}")
    vm_data = virtual_machines.get_instances(project_id)
    virtual_machines.upload_vm_data_to_bigquery(vm_data, project_id)

    return {
        "project_id": project_id,
        "compute": vm_data,
        "storage": {"buckets": bucket_inventory.get_buckets(project_id)},
        "snapshots": {"snapshots": snapshot_inventory.get_snapshots(project_id)},
        "orphaned": {"disks": orphaned_disks.get_orphaned_disks(project_id)},
        "schedules": {"schedules": snapshot_schedule_report.get_snapshot_schedules(project_id)},
        "utilization": {"metrics": metrics_utilization.get_metrics(project_id)}
    }


def run_inventory():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_project, project_ids))

    vm_counts = []

    for result in results:
        pid = result["project_id"]

        upload_json_to_gcs(BUCKET_NAME, result, pid)

        vm_counts.append((pid, len(result["compute"])))

        context = {
            'project_id': pid,
            'compute_resources': {pid: {"vms": result["compute"]}},
            'storage_resources': {pid: result["storage"]},
            'snapshot_resources': {pid: result["snapshots"]},
            'orphaned_disks': {pid: result["orphaned"]},
            'snapshot_schedule': {pid: result["schedules"]},
            'utilization_metrics': {pid: result["utilization"]},
            'vm_counts': [(pid, len(result["compute"]))]
        }

        section_html = render_project_section(context)
        section_path = os.path.join(output_dir, f"{pid}.html")
        with open(section_path, "w") as f:
            f.write(section_html)

    # Merge all individual sections into one dashboard
    merged_sections = ""
    for pid in project_ids:
        section_path = os.path.join(output_dir, f"{pid}.html")
        with open(section_path, "r") as f:
            merged_sections += f.read()
        os.remove(section_path)

    # Generate final dashboard
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dashboard_{timestamp}.html"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w") as f:
        f.write(generate_html({"content": merged_sections}))

    print(f"Dashboard generated at: {output_path}")
    upload_to_gcs(BUCKET_NAME, output_path, f"reports/{filename}")
    os.remove(output_path)
    print(f"Deleted local file: {output_path}")


if __name__ == "__main__":
    run_inventory()