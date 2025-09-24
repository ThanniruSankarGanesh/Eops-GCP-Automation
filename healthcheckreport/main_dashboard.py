import os
import service_health_report
import snapshot_schedule_report
import snapshot_report
import unattached_disk_report
import disk_report
import buckets_report
import cloud_armor_report
import shared_vpc
import vpc_report
import vpc_peering_report
import health_check_report
from google.cloud import storage

json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
 
# HTML Dashboard with full-page tabs
def generate_dashboard_html():
    health_data = service_health_report.generate_service_health_report()
    schedule_data = snapshot_schedule_report.generate_snapshot_schedule_report()
    snapshot_data = snapshot_report.generate_snapshot_report()
    unattached_disk_data = unattached_disk_report.generate_unattached_disk_report()
    disk_data = disk_report.generate_disk_report()
    buckets_data = buckets_report.generate_buckets_report()
    policies_data = cloud_armor_report.generate_cloud_armor_report()
    shared_vpc_data = shared_vpc.generate_shared_vpc_report()
    vpc_data = vpc_report.generate_vpc_report()
    vpc_peering_data = vpc_peering_report.generate_vpc_peering_report()
    all_health_checks_data = health_check_report.generate_health_check_report()
 
    html_content = """
    <html>
    <head>
        <title>Daily Health Check Up Report</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
                margin: 0;
                padding: 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
            }
            .tab-button {
                display: inline-block;
                margin: 10px;
                padding: 10px 20px;
                background-color: #6c757d;
                color: white;
                cursor: pointer;
                border-radius: 4px;
                border: none;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }
            .tab-button:hover {
                background-color: #5a6268;
            }
.tab-button.active {
                background-color: #007bff;
                color: white;
            }
            .tab-content {
                display: none;
                padding: 20px;
                border-radius: 8px;
                background-color: #ffffff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
.tab-content.active {
                display: block;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                table-layout: auto;
            }
            th, td {
                border: 1px solid #dee2e6;
                padding: 12px;
                text-align: left;
                min-width: 200px;
            }
            th {
                background-color: #007bff;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #e9ecef;
            }
            tr td:first-child {
                font-weight: bold;
            }
        </style>
        <script>
            function openTab(tabId) {
                var tabs = document.getElementsByClassName('tab-content');
                var buttons = document.getElementsByClassName('tab-button');
 
                // Hide all tab contents and remove active class from all buttons
                for (var i = 0; i < tabs.length; i++) {
                    tabs[i].classList.remove('active');
                }
                for (var i = 0; i < buttons.length; i++) {
                    buttons[i].classList.remove('active');
                }
 
                // Show the clicked tab content and make the button active
                document.getElementById(tabId).classList.add('active');
                event.currentTarget.classList.add('active');                
            }
        </script>
    </head>
    <body>
        <h1>GCP Health Check Dashboard</h1>
        <div class="tab-buttons">
            <button class="tab-button active" onclick="openTab('serviceHealth')">Service Health Report</button>
            <button class="tab-button" onclick="openTab('snapshotSchedule')">Snapshot Schedule Report</button>
            <button class="tab-button" onclick="openTab('snapshot')">Snapshot Report</button>
            <button class="tab-button" onclick="openTab('unattachedDisk')">Unattached Disk Report</button>
            <button class="tab-button" onclick="openTab('disk')">Disk Report</button>
            <button class="tab-button" onclick="openTab('bucket')">Bucket Report</button>
            <button class="tab-button" onclick="openTab('policy')">Cloud Armor Report</button>
            <button class="tab-button" onclick="openTab('xpnProjectStatus')">Shared VPC Report</button>
            <button class="tab-button" onclick="openTab('network')">VPC Report</button>
            <button class="tab-button" onclick="openTab('peering')">VPC Peering Report</button>
            <button class="tab-button" onclick="openTab('healthCheck')">Health Check Report</button>
        </div>
 
        <div id="serviceHealth" class="tab-content active">
            <h2>Service Health Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Event ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>State</th>
                    <th>Relevance</th>
                    <th>Update Time</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Detailed State</th>
                    <th>Product</th>
                    <th>Location</th>
                </tr>
    """
 
    for event in health_data:
        html_content += f"""
            <tr>
                <td>{event['Project ID']}</td>
                <td>{event['Event ID']}</td>
                <td>{event['Title']}</td>
                <td>{event['Description']}</td>
                <td>{event['Category']}</td>
                <td>{event['State']}</td>
                <td>{event['Relevance']}</td>
                <td>{event['Update Time']}</td>
                <td>{event['Start Time']}</td>
                <td>{event['End Time']}</td>
                <td>{event['Detailed State']}</td>
                <td>{event['Product']}</td>
                <td>{event['Location']}</td>
            </tr>
        """
 
    html_content += """
            </table>
        </div>
 
        <div id="snapshotSchedule" class="tab-content">
            <h2>Snapshot Schedule Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Name</th>
                    <th>Region</th>
                    <th>Status</th>
                    <th>Storage Location</th>
                    <th>Schedule Frequency</th>
                    <th>Auto-delete Snapshots After</th>
                </tr>
    """
 
    for schedule in schedule_data:
        html_content += f"""
            <tr>
                <td>{schedule['Project ID']}</td>
                <td>{schedule['Name']}</td>
                <td>{schedule['Region']}</td>
                <td>{schedule['Status']}</td>
                <td>{schedule['Storage Location']}</td>
                <td>{schedule['Schedule Frequency']}</td>
                <td>{schedule['Auto-delete Snapshots After']}</td>
            </tr>
        """
 
    html_content += """
            </table>
        </div>
 
        <div id="snapshot" class="tab-content">
            <h2>Snapshot Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Size (GB)</th>
                    <th>Creation Date</th>
                    <th>Source Disk</th>
                    <th>Age (days)</th>
                    <th>Creation Type</th>
                </tr>
    """
 
    for snapshot in snapshot_data:
        html_content += f"""
            <tr>
                <td>{snapshot['Project ID']}</td>
                <td>{snapshot['Name']}</td>
                <td>{snapshot['Status']}</td>
                <td>{snapshot['Size (GB)']}</td>
                <td>{snapshot['Creation Date']}</td>
                <td>{snapshot['Source Disk']}</td>
                <td>{snapshot['Age (days)']}</td>
                <td>{snapshot['Creation Type']}</td>
            </tr>
        """
 
    html_content += """
            </table>
        </div>
 
        <div id="unattachedDisk" class="tab-content">
            <h2>Unattached Disk Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Name</th>
                    <th>Size (GB)</th>
                    <th>Creation Date</th>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Zone</th>
                    <th>Users</th>
                    <th>Description</th>
                </tr>
    """
 
    for disk in unattached_disk_data:
        html_content += f"""
            <tr>
                <td>{disk['Project ID']}</td>
                <td>{disk['Name']}</td>
                <td>{disk['Size (GB)']}</td>
                <td>{disk['Creation Date']}</td>
                <td>{disk['Status']}</td>
                <td>{disk['Type']}</td>
                <td>{disk['Zone']}</td>
                <td>No Users</td>
                <td>{disk['Description']}</td>
            </tr>
        """
 
    html_content += """
            </table>
        </div>
 
        <div id="disk" class="tab-content">
            <h2>Disk Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Disk Name</th>
                    <th>Size (GB)</th>
                    <th>Type</th>
                    <th>Creation Timestamp</th>
                    <th>Zone</th>
                    <th>Status</th>
                    <th>Users</th>
                    <th>Description</th>
                </tr>
    """
 
    for disk in disk_data:
        html_content += f"""
            <tr>
                <td>{disk['Project ID']}</td>
                <td>{disk['Name']}</td>
                <td>{disk['Size (GB)']}</td>
                <td>{disk['Type']}</td>
                <td>{disk['Creation Date']}</td>
                <td>{disk['Zone']}</td>
                <td>{disk['Status']}</td>
                <td>{disk['Users']}</td>
                <td>{disk['Description']}</td>
            </tr>
        """
    html_content += """
            </table>
        </div>

        <div id="bucket" class="tab-content">
            <h2>Bucket  Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Bucket Name</th>
                    <th>Location</th>
                    <th>Location Type</th>
                    <th>Storage Class</th>
                    <th>Created Time</th>
                    <th>Last Updated Time</th>
                    <th>Versioning Enabled</th>
                    <th>Labels</th>
                    <th>Soft Deleted Policy Effective Date</th>
                    <th>Retention Period (days)</th>
                    <th>Access Control</th>
                </tr>
    """

    for bucket in buckets_data:
        html_content += f"""
            <tr>
                <td>{bucket['Project ID']}</td>
                <td>{bucket['Bucket Name']}</td>
                <td>{bucket['Location']}</td>
                <td>{bucket['Location Type']}</td>
                <td>{bucket['Storage Class']}</td>
                <td>{bucket['Created Time']}</td>
                <td>{bucket['Last Updated Time']}</td>
                <td>{bucket['Versioning Enabled']}</td>
                <td>{bucket['Labels']}</td>
                <td>{bucket['Soft Deleted Policy Effective Date']}</td>
                <td>{bucket['Retention Period (days)']}</td>
                <td>{bucket['Access Control']}</td>
            </tr>
        """
    html_content += """
            </table>
        </div>

        <div id="policy" class="tab-content">
            <h2>Cloud Armor Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Policy Name</th>
                    <th>Description</th>
                    <th>Type</th>
                    <th>Scope</th>
                    <th>Rules</th>
                </tr>
    """

    for policy in policies_data:
        html_content += f"""
            <tr>
                <td>{policy['Project ID']}</td>
                <td>{policy['Policy Name']}</td>
                <td>{policy['Description']}</td>
                <td>{policy['Type']}</td>
                <td>{policy['Scope']}</td>
                <td>
                    <ul>
                    {''.join(f"<li>Priority: {rule['priority']}, Action: {rule['action']}, Match: {rule['match']}, Applies to: {rule['applies_to']}</li>" for rule in policy['rules'])}
                    </ul>
                </td>
            </tr>
        """
    html_content += """
            </table>
        </div>

        <div id="xpnProjectStatus" class="tab-content">
            <h2>Shared VPC Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Name</th>
                    <th>ID</th>
                    <th>Creation Timestamp</th>
                    <th>Project Status</th>
                </tr>
    """

    for svpc in shared_vpc_data:
        html_content += f"""
            <tr>
                <td>{svpc['Project ID']}</td>
                <td>{svpc['Name']}</td>
                <td>{svpc['ID']}</td>
                <td>{svpc['Creation Timestamp']}</td>
                <td>{svpc['Project Status']}</td>
            </tr>
        """
        html_content += """
            </table>
        </div>

        <div id="network" class="tab-content">
            <h2>VPC Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Network Name</th>
                    <th>Auto Create Subnetworks</th>
                    <th>Creation Time</th>
                    <th>Subnetwork Name</th>
                    <th>IP Range</th>
                    <th>Region</th>
                </tr>
    """

    for vpc in vpc_data:
        subnetworks = vpc.get('Subnetworks', [])
        if subnetworks:
            for subnet in subnetworks:
                html_content += f"""
                    <tr>
                        <td>{vpc['Project ID']}</td>
                        <td>{vpc['Network Name']}</td>
                        <td>{vpc['Auto Create Subnetworks']}</td>
                        <td>{vpc['Creation Time']}</td>
                        <td>{subnet.get('Subnetwork Name')}</td>
                        <td>{subnet.get('IP Range', 'N/A')}</td>
                        <td>{subnet.get('Region', 'N/A')}</td>
                    </tr>
                """
        else:
            html_content += f"""
                <tr>
                    <td>{vpc['Project ID']}</td>
                    <td>{vpc['Network Name']}</td>
                    <td>{vpc['Auto Create Subnetworks']}</td>
                    <td>{vpc['Creation Time']}</td>
                </tr>
            """
    html_content += """
            </table>
        </div>

        <div id="peering" class="tab-content">
            <h2>VPC Peering Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Network Name</th>
                    <th>Peering Name</th>
                    <th>Peered Network</th>
                    <th>Peering State</th>
                    <th>Exchange Subnet Routes</th>
                    <th>Auto Create Routes</th>
                    <th>Export Custom Routes</th>
                    <th>Import Custom Routes</th>
                </tr>
    """

    for peering in vpc_peering_data:
        html_content += f"""
            <tr>
                <td>{peering['Project ID']}</td>
                <td>{peering['Network Name']}</td>
                <td>{peering['Peering Name']}</td>
                <td>{peering['Peered Network']}</td>
                <td>{peering['Peering State']}</td>
                <td>{peering['Exchange Subnet Routes']}</td>
                <td>{peering['Auto Create Routes']}</td>
                <td>{peering['Export Custom Routes']}</td>
                <td>{peering['Import Custom Routes']}</td>
            </tr>
        """
    html_content += """
            </table>
        </div>

        <div id="healthCheck" class="tab-content">
            <h2>Health Check Report</h2>
            <table>
                <tr>
                    <th>Project ID</th>
                    <th>Name</th>
                    <th>In use by</th>
                    <th>Protocol</th>
                    <th>Port</th>
                    <th>Port specification</th>
                    <th>Proxy protocol</th>
                    <th>Interval</th>
                    <th>Timeout</th>
                    <th>Healthy threshold</th>
                    <th>Unhealthy threshold</th>
                    <th>Scope</th>
                    <th>Region</th>
                </tr>
    """
    for healthCheck in all_health_checks_data:
        html_content += f"""
            <tr>
                <td>{healthCheck['Project ID']}</td>
                <td>{healthCheck['Name']}</td>
                <td>{healthCheck['In use by']}</td>
                <td>{healthCheck['Protocol']}</td>
                <td>{healthCheck['Port']}</td>
                <td>{healthCheck['Port specification']}</td>
                <td>{healthCheck['Proxy protocol']}</td>
                <td>{healthCheck['Interval']}</td>
                <td>{healthCheck['Timeout']}</td>
                <td>{healthCheck['Healthy threshold']}</td>
                <td>{healthCheck['Unhealthy threshold']}</td>
                <td>{healthCheck['Scope']}</td>
                <td>{healthCheck['Region']}</td>
            </tr>
        """ 
    html_content += """
            </table>
        </div>
 
    </body>
    </html>
    """
 
    return html_content



def upload_to_bucket(bucket_name, source_file_name, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"✅ Uploaded {source_file_name} to gs://{bucket_name}/{destination_blob_name}")

if __name__ == '__main__':
    dashboard_html = generate_dashboard_html()
    local_file = 'gcp_health_check_dashboard.html'
    with open(local_file, 'w') as f:
        f.write(dashboard_html)

    # Replace with your actual bucket name and desired path
    bucket_name = 'gcp_cloud_dashboard'
    destination_blob_name = 'reports/gcp_health_check_dashboard.html'

    upload_to_bucket(bucket_name, local_file, destination_blob_name)

 

# Save the dashboard as an HTML file
if __name__ == '__main__':
    dashboard_html = generate_dashboard_html()
    with open('gcp_health_check_dashboard.html', 'w') as f:
        f.write(dashboard_html)