import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, "key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

project_ids = ['eops-gcp-lab']

BUCKET_NAME = "gcp_cloud_dashboard"
 