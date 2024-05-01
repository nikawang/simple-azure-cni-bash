# token=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F" | jq -r .access_token)

# # 获取VM的元数据
# metadata=$(curl -s -H Metadata:true -H "Authorization: Bearer $token" "http://169.254.169.254/metadata/instance?api-version=2020-09-01")
# networkInterfaceId=$(echo $metadata | jq -r '.network.interface[0]')


import os
import json
import ipaddress
import requests

token_url = "http://169.254.169.254/metadata/identity/oauth2/token"
token_params = {
    'api-version': '2018-02-01',
    'resource': 'https://management.azure.com/'
}
token_headers = {
    'Metadata': 'true'
}
token_response = requests.get(token_url, headers=token_headers, params=token_params)
token = token_response.json().get('access_token')

metadata_url = "http://169.254.169.254/metadata/instance"
metadata_params = {
    'api-version': '2020-09-01'
}
metadata_headers = {
    'Metadata': 'true',
    'Authorization': f'Bearer {token}'
}
metadata_response = requests.get(metadata_url, headers=metadata_headers, params=metadata_params)
metadata = metadata_response.json()

vm_name = metadata.get('compute', {}).get('name')
resource_group = metadata.get('compute', {}).get('resourceGroupName')
subscription_id = metadata.get('compute', {}).get('subscriptionId')
nic_info =  metadata.get('network', {}).get('interface', [{}])[0]

subnet_info = nic_info['ipv4']['subnet'][0]
subnet_address = subnet_info['address']
subnet_prefix = subnet_info['prefix']


subnet_cidr = f"{subnet_address}/{subnet_prefix}"

subnet = ipaddress.ip_network(subnet_cidr, strict=False)
first_address = str(subnet.network_address + 1)

data_to_write = {
    "vm_name": vm_name,
    "resource_group": resource_group,
    "subscription_id": subscription_id,
    "subnet_cidr": subnet_cidr,
    "subnet_gw_ip": first_address
}


output_filename = "subnet_info.json"
output_path = os.path.join("/etc/cni/net.d", output_filename)

try:
    with open(output_path, 'w') as outfile:
        json.dump(data_to_write, outfile)
    print(f"Data written to {output_path}")
except PermissionError:
    print("Permission denied: You need to run this script as root or with sudo.")
except Exception as e:
    print(f"An error occurred: {e}")