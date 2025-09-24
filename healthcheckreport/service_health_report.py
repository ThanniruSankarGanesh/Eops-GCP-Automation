import os
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(json_keyfile, scopes=['https://www.googleapis.com/auth/cloud-platform'])

    auth_req = Request()
    credentials.refresh(auth_req)
    return credentials.token

def generate_service_health_report():
    token = get_access_token()

    all_events = []
    for project_id in project_ids:
        url = f'https://servicehealth.googleapis.com/v1/projects/{project_id}/locations/global/events'
        response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

        if response.status_code == 404:
            continue
        elif response.status_code != 200:
            continue

        events = response.json().get('events', [])
        for event in events:
            if 'eventImpacts' in event and event['eventImpacts']:
                product_name = event['eventImpacts'][0]['product']['productName']
                location_name = event.get('eventImpacts')[0].get('location', {}).get('locationName')
                event_id = event.get('name').split('/')[-1]

                all_events.append({
                    "Project ID": project_id,
                    "Event ID": event_id,
                    "Title": event.get('title'),
                    "Description": event.get('description'),
                    "Category": event.get('category'),
                    "State": event.get('state'),
                    "Relevance": event.get('relevance'),
                    "Update Time": event.get('updateTime'),
                    "Start Time": event.get('startTime'),
                    "End Time": event.get('endTime'),
                    "Detailed State": event.get('detailedState'),
                    "Product": product_name,
                    "Location": location_name
                })

    return all_events