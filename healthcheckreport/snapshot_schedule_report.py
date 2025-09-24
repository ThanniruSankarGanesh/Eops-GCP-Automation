import os
import json
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def generate_snapshot_schedule_report():
    def get_snapshot_schedules(project):
        try:
            command = f'gcloud compute resource-policies list --format=json --project={project}'
            result = os.popen(command).read()
            snapshot_schedules = json.loads(result)
            return snapshot_schedules
        except Exception as e:
            return []

    snapshot_schedule_data = []
    for project in project_ids:
        schedules = get_snapshot_schedules(project)
        if not schedules:
            continue

        for schedule in schedules:
            name = schedule.get('name', 'N/A')
            region = schedule.get('region', 'N/A').split('/')[-1]
            status = schedule.get('status', 'N/A')

            schedule_policy = schedule.get('snapshotSchedulePolicy', {})
            retention_policy = schedule_policy.get('retentionPolicy', {})
            schedule_config = schedule_policy.get('schedule', {})
            snapshot_properties = schedule_policy.get('snapshotProperties', {})
            storage_location = snapshot_properties.get('storageLocations', ['N/A'])[0]

            hours_in_cycle = schedule_config.get('hourlySchedule', {}).get('hoursInCycle')
            days_in_cycle = schedule_config.get('dailySchedule', {}).get('daysInCycle')
            start_time = schedule_config.get('hourlySchedule', {}).get('startTime', 'N/A')

            if hours_in_cycle is not None:
                frequency = f"Every {hours_in_cycle} hour(s), starting at {start_time} UTC"
            elif days_in_cycle is not None:
                frequency = f"Every {days_in_cycle} day(s)"
            else:
                frequency = "N/A"
            
            max_retention_days = retention_policy.get('maxRetentionDays', 'N/A')

            snapshot_schedule_data.append({
                "Project ID": project,
                "Name": name,
                "Region": region,
                "Status": status,
                "Storage Location": storage_location,
                "Schedule Frequency": frequency,
                "Auto-delete Snapshots After": max_retention_days
            })

    return snapshot_schedule_data