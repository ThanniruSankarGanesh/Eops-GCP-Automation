import os
from googleapiclient.discovery import build
from config import project_ids

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def get_cloud_armor_policies(project_id):
    service = build('compute', 'v1')
    request = service.securityPolicies().list(project=project_id)
    response = request.execute()
    return response.get('items', [])
 
def generate_cloud_armor_report():
    policies_data = []
    for project_id in project_ids:
        policies = get_cloud_armor_policies(project_id)
        if policies:
            for policy in policies:
                self_link = policy.get('selfLink', 'No selfLink')
                scope = self_link.split('/')[7] if 'global' in self_link or 'regions' in self_link else 'Unknown'

                policy_details = {
                    'Project ID': project_id,
                    'Policy Name': policy.get('name', 'No name'),
                    'Description': policy.get('description', 'No description'),
                    'Type': policy.get('type', 'No type'),
                    'Scope': scope,
                    'rules': []
                }
                # Check and log the rules for this policy
                rules = policy.get('rules', [])
                if rules:
                    for rule in rules:
                        rule_details = {
                            'priority': rule.get('priority', 'No priority'),
                            'action': rule.get('action', 'No action'),
                            'match': rule.get('match', {}).get('config', {}).get('srcIpRanges', 'No match'),
                            'applies_to': rule.get('match', {}).get('versionedExpr', 'No versioned expression'),
                            'description': rule.get('description', 'No description')
                        }
                        policy_details['rules'].append(rule_details)
                else:
                    print(f"No rules found for policy {policy.get('name', 'Unnamed')} in project {project_id}")
                policies_data.append(policy_details)
        else:
            print(f"No Cloud Armor policies found for project {project_id}.")
    return policies_data