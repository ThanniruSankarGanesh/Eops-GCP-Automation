import os
from googleapiclient.discovery import build
from google.auth import default
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def generate_vpc_report():
    def get_vpc_details():
        credentials, project = default()
        service = build('compute', 'v1', credentials=credentials)
        
        vpc_data = []
        for project_id in project_ids:
            print(f"Fetching VPC networks for project: {project_id}")
            request = service.networks().list(project=project_id)
            response = request.execute()
            networks = response.get('items', [])
            if not networks:
                print(f"No VPC networks found for project: {project_id}")
            else:
                for network in networks:
                    essential_info = {
                        "Project ID": project_id,
                        "Network Name": network.get('name'),
                        "Auto Create Subnetworks": network.get('autoCreateSubnetworks'),
                        "Creation Time": network.get('creationTimestamp'),
                        "Subnetworks": []
                    }
                    # Fetch all regions to check for subnetworks
                    if not network['autoCreateSubnetworks']:
                        regions_request = service.regions().list(project=project_id)
                        regions_response = regions_request.execute()
                        regions = regions_response.get('items', [])
                        for region in regions:
                            region_name = region['name']
                            subnet_request = service.subnetworks().list(project=project_id, region=region_name)
                            subnet_response = subnet_request.execute()
                            subnetworks = subnet_response.get('items', [])
                            
                            if subnetworks:
                                for subnetwork in subnetworks:
                                    if subnetwork['network'].endswith(network['name']):
                                        essential_info["Subnetworks"].append({
                                            "Subnetwork Name": subnetwork.get('name'),
                                            "IP Range": subnetwork.get('ipCidrRange'),
                                            "Region": region_name,
                                        })
                    vpc_data.append(essential_info)
        return vpc_data
    return get_vpc_details()