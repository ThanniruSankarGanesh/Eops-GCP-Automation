import os
from googleapiclient.discovery import build
from google.auth import default
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def generate_vpc_peering_report():
    def get_vpc_peering_details():
        credentials, project = default()
        service = build('compute', 'v1', credentials=credentials)

        vpc_peering_data = []

        for project_id in project_ids:
            print(f"Fetching VPC peering connections for project: {project_id}")

            network_request = service.networks().list(project=project_id)
            network_response = network_request.execute()
            networks = network_response.get('items', [])

            if not networks:
                print(f"No VPC networks found for project: {project_id}")
            else:
                for network in networks:
                    network_name = network.get('name')
                    peerings = network.get('peerings', [])
                
                    if not peerings:
                        print(f"No peerings found for network: {network_name} in project: {project_id}")
                    else:
                        for peering in peerings:
                            peered_network_url = peering.get('network')
                            peered_network_name = peered_network_url.split('/')[-1]

                            peering_info = {
                                "Project ID": project_id,
                                "Network Name": network_name,
                                "Peering Name": peering.get('name'),
                                "Peered Network": peered_network_name,
                                "Peering State": peering.get('state'),
                                "Exchange Subnet Routes": peering.get('exchangeSubnetRoutes'),
                                "Auto Create Routes": peering.get('autoCreateRoutes'),
                                "Export Custom Routes": peering.get('exportCustomRoutes'),
                                "Import Custom Routes": peering.get('importCustomRoutes') 
                            }

                            vpc_peering_data.append(peering_info)
        return vpc_peering_data
    return get_vpc_peering_details()