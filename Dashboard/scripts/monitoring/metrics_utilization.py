from google.cloud import monitoring_v3
from datetime import datetime, timedelta, timezone

def get_metrics(project_id):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    end_time = datetime.now(tz=timezone.utc)
    start_time = end_time - timedelta(days=1)  # last 24 hours

    interval = monitoring_v3.TimeInterval(
        end_time=end_time,
        start_time=start_time
    )

    aggregation = monitoring_v3.Aggregation(
        alignment_period=timedelta(minutes=30),
        per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
    )

    metrics = {}

    def fetch_metric(metric_type):
        return client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type = "{metric_type}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation,
            }
        )

    # CPU utilization
    cpu_data = fetch_metric("compute.googleapis.com/instance/cpu/utilization")
    cpu = []
    for series in cpu_data:
        instance_id = series.resource.labels.get("instance_id", "unknown")
        avg_value = series.points[0].value.double_value if series.points else 0
        cpu.append({
            "instance_id": instance_id,
            "cpu_utilization": round(avg_value * 100, 2)
        })
    metrics["cpu"] = cpu

    # Memory utilization
    mem_data = fetch_metric("agent.googleapis.com/memory/percent_used")
    mem = []
    for series in mem_data:
        instance_id = series.resource.labels.get("instance_id", "unknown")
        avg_value = series.points[0].value.double_value if series.points else 0
        mem.append({
            "instance_id": instance_id,
            "memory_percent_used": round(avg_value, 2)
        })
    metrics["memory"] = mem

    return metrics
