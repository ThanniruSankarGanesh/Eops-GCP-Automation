import json
import os
import subprocess
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
 
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e.stderr.decode()}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON output: {e}")
        return None
 
def get_valid_regions(project_id):
    command = f'gcloud compute regions list --project={project_id} --format=json'
    valid_regions = run_command(command)
    
    if valid_regions is None:
        return []
 
    return [region['name'] for region in valid_regions]
 
def get_backend_services_using_health_check(project_id, health_check_name, scope, region):
    backend_services_in_use = []
 
    # Check if the region is valid for the project
    valid_regions = get_valid_regions(project_id)
    if region and region not in valid_regions:
        print(f"Warning: The specified region '{region}' is not valid for project '{project_id}'. Using global services instead.")
        scope = 'global'
 
    command = (f'gcloud compute backend-services list --{"global" if scope == "global" else "regions=" + region} '
               f'--project={project_id} --format=json')
    backend_services = run_command(command)
    
    if backend_services is None:
        return backend_services_in_use
 
    for service in backend_services:
        health_checks = service.get('healthChecks', [])
        for hc in health_checks:
            if health_check_name in hc:
                backend_services_in_use.append(service.get('name', ''))
 
    return backend_services_in_use
 
def get_serving_port(project_id, backend_service_name, scope, region):
    if scope == 'global':
        command = f'gcloud compute backend-services describe {backend_service_name} --global --project={project_id} --format=json'
    else:
        command = f'gcloud compute backend-services describe {backend_service_name} --region={region} --project={project_id} --format=json'
 
    backend_service = run_command(command)
    if backend_service is None:
        return 80  # Default to port 80 if the backend service can't be retrieved
 
    return backend_service.get('port', 80)  # Default to port 80 if not explicitly set
 
def generate_health_check_report():
    all_health_checks_data = []
 
    for project_id in project_ids:
        command = (f'gcloud compute health-checks list --project={project_id} '
                   f'--format="json(name, type, tcpHealthCheck, httpHealthCheck, httpsHealthCheck, sslHealthCheck, udpHealthCheck, proxyHeader, checkIntervalSec, timeoutSec, healthyThreshold, unhealthyThreshold, region, selfLink)"')
        health_checks = run_command(command)
 
        if health_checks is None:
            continue
 
        for health_check in health_checks:
            health_check_name = health_check.get('name', '')
            scope = 'global' if 'global' in health_check.get('selfLink', '') else 'regional'
            region = health_check.get('region', '').split('/')[-1] if 'region' in health_check else ''
 
            # Fetch 'In use by' data from backend services
            in_use_by_list = get_backend_services_using_health_check(project_id, health_check_name, scope, region)
            in_use_by = ', '.join(in_use_by_list) if in_use_by_list else 'N/A'
 
            # Determine the port and handle USE_SERVING_PORT case
            port = (health_check.get('tcpHealthCheck', {}).get('port') or
                    health_check.get('httpHealthCheck', {}).get('port') or
                    health_check.get('httpsHealthCheck', {}).get('port') or
                    health_check.get('sslHealthCheck', {}).get('port') or
                    health_check.get('udpHealthCheck', {}).get('port'))
 
            # If port is not set, check for USE_SERVING_PORT specification
            port_specification = (health_check.get('tcpHealthCheck', {}).get('portSpecification') or
                                  health_check.get('httpHealthCheck', {}).get('portSpecification') or
                                  health_check.get('httpsHealthCheck', {}).get('portSpecification') or
                                  health_check.get('sslHealthCheck', {}).get('portSpecification') or
                                  health_check.get('udpHealthCheck', {}).get('portSpecification'))
 
            if port_specification == "USE_SERVING_PORT" and in_use_by_list:
                port = get_serving_port(project_id, in_use_by_list[0], scope, region)
 
            # Proxy protocol, if set
            proxy_protocol = health_check.get('proxyHeader', 'NONE')  # Default to NONE if not set
 
            all_health_checks_data.append({
                'Project ID': project_id,
                'Name': health_check_name,
                'In use by': in_use_by,
                'Protocol': health_check.get('type', ''),
                'Port': port,
                'Port specification': port_specification,
                'Proxy protocol': proxy_protocol,
                'Interval': health_check.get('checkIntervalSec', ''),
                'Timeout': health_check.get('timeoutSec', ''),
                'Healthy threshold': health_check.get('healthyThreshold', ''),
                'Unhealthy threshold': health_check.get('unhealthyThreshold', ''),
                'Scope': scope,
                'Region': region
            })
 
    return all_health_checks_data