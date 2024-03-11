from flask import Flask, request, jsonify, render_template
from netaddr import IPNetwork, IPSet
from pandas import pandas as pd

def json_to_html_table(json_data):
    # Convert JSON data to pandas DataFrame
    azure_vnet_ip_range_df = pd.DataFrame([json_data['azure_vnet_ip_range']], columns=['cidr', 'start_end_ip', 'total_ips'])
    existing_subnets_df = pd.DataFrame(json_data['existing_subnets'], columns=['cidr', 'start_end_ip', 'total_ips'])
    suitable_ip_range_df = pd.DataFrame([{'cidr': json_data['suitable_ip_range'], 'start_end_ip': json_data['start_end_ip'], 'total_ips': json_data['total_ips']}])

    # Convert DataFrames to HTML tables
    azure_vnet_ip_range_html = azure_vnet_ip_range_df.to_html(index=False)
    existing_subnets_html = existing_subnets_df.to_html(index=False)
    suitable_ip_range_html = suitable_ip_range_df.to_html(index=False)

    return azure_vnet_ip_range_html, existing_subnets_html, suitable_ip_range_html

def json_to_html_table(json_data):
    # Convert JSON data to pandas DataFrame
    azure_vnet_ip_range_df = pd.DataFrame([json_data['azure_vnet_ip_range']], columns=['cidr', 'start_end_ip', 'total_ips'])
    existing_subnets_df = pd.DataFrame(json_data['existing_subnets'], columns=['cidr', 'start_end_ip', 'total_ips'])
    suitable_ip_range_df = pd.DataFrame([{'cidr': json_data['suitable_ip_range'], 'start_end_ip': json_data['start_end_ip'], 'total_ips': json_data['total_ips']}])

    # Convert DataFrames to HTML tables
    azure_vnet_ip_range_html = azure_vnet_ip_range_df.to_html(index=False)
    existing_subnets_html = existing_subnets_df.to_html(index=False)
    suitable_ip_range_html = suitable_ip_range_df.to_html(index=False)

    return azure_vnet_ip_range_html, existing_subnets_html, suitable_ip_range_html

app = Flask(__name__)
app.json.sort_keys = False

def convert_to_list(existing_cidrs):
    # Check if there are multiple existing cidrs are added
    if "," in existing_cidrs:
        return existing_cidrs.split(",")
    else:
        return [existing_cidrs]
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        cidr = request.form["vnet_iprange"]
        existing_cidrs = request.form.get("subnet_ipranges", "")
        required_ips = int(request.form["required_ips"]) + 5  # Add 5 to account for Azure's reserved addresses   
        all_ips = IPSet(IPNetwork(cidr))

        sorted_existing_cidrs = []
        for existing_cidr in existing_cidrs:
            existing_network = IPNetwork(existing_cidr)
            sorted_existing_cidrs.append(existing_network)
        
        existing_cidrs_info = []
        for sorted_existing_cidr in sorted(sorted_existing_cidrs):
            existing_network = IPNetwork(sorted_existing_cidr)
            sorted_existing_cidrs.append(existing_network)
            print("remove existing network: " + str(existing_network))
            all_ips.remove(existing_network)
            existing_cidrs_info.append({
                "cidr": str(existing_network),
                "start_end_ip": f"{str(existing_network.network)} - {str(existing_network.broadcast)}",
                "total_ips": len(existing_network)
            })
        
        # Calculate total IPs in the CIDR and existing CIDRs
        total_ips_in_cidr = len(IPNetwork(cidr))
        if existing_cidrs:
            total_ips_in_existing_cidrs = sum(len(IPNetwork(existing_cidr)) for existing_cidr in convert_to_list(existing_cidrs))
        else:
            total_ips_in_existing_cidrs = 0

        # Check if the required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR
        if required_ips + total_ips_in_existing_cidrs > total_ips_in_cidr:
            return render_template('error.html', error_message='The required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR')
    
        # Iterate all_ips and find suitable_range based on the required number of ip addresses
        suitable_range = None
        start_ip = None
        end_ip = None
        suitable_ips = 0
        for ip in all_ips.iter_cidrs():
            subnet = IPNetwork(ip)
            subnet_size = len(subnet)
            if subnet_size >= required_ips:
                suitable_range = str(subnet.cidr)
                start_ip = str(subnet.network)
                end_ip = str(subnet.broadcast)
                suitable_ips = subnet_size
                break
    
        ip_ranges = {
            "cidr": cidr,
            "start_end_ip": f"{str(IPNetwork(cidr).network)} - {str(IPNetwork(cidr).broadcast)}",
            "total_ips": len(IPNetwork(cidr))
        }

        # Create a dictionary
        data = {
            "azure_vnet_ip_range": ip_ranges,
            "existing_subnets": existing_cidrs_info,
            "start_end_ip": f"{start_ip} - {end_ip}",
            "suitable_ip_range": suitable_range,
            "total_ips": suitable_ips
        }

        # Convert the dictionary to a JSON response
        json_data = jsonify(data)

        # Convert the dictionary to HTML tables
        azure_vnet_ip_range_html, existing_subnets_html, suitable_ip_range_html = json_to_html_table(data)

        print(azure_vnet_ip_range_html)
        print(existing_subnets_html)
        print(suitable_ip_range_html)
        
        return render_template('result.html', azure_vnet_ip_range=azure_vnet_ip_range_html, existing_subnets=existing_subnets_html, suitable_ip_range=suitable_ip_range_html)
            
        #return jsonify({"azure_vnet_ip_range": ip_ranges, "existing_subnets": existing_cidrs_info, "start_end_ip": f"{start_ip} - {end_ip}", "suitable_ip_range": suitable_range, "total_ips": suitable_ips})
        
    return render_template("home.html")