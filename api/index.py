from flask import Flask, request, jsonify, render_template
from netaddr import IPNetwork, IPSet
from pandas import pandas as pd
import math

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

def smallest_subnet_size(required_ips):
    # Calculate the smallest subnet size that can fit the required IPs
    return 32 - math.ceil(math.log2(required_ips))

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
        json_output = 'json_output' in request.form

        # Variables
        total_ips_in_existing_cidrs = 0
        total_ips_in_cidr = len(IPNetwork(cidr)) # Total IPs in the CIDR
        
        # Check if there are existing Subnet Ranges    
        if existing_cidrs:
            sorted_existing_cidrs = []
            for existing_cidr in convert_to_list(existing_cidrs):
                existing_network = IPNetwork(existing_cidr)
                sorted_existing_cidrs.append(existing_network)

            existing_cidrs_info = []    
            for sorted_existing_cidr in sorted(sorted_existing_cidrs):
                existing_network = IPNetwork(sorted_existing_cidr)
                all_ips.remove(existing_network)
                existing_cidrs_info.append({
                    "cidr": str(existing_network),
                    "start_end_ip": f"{str(existing_network.network)} - {str(existing_network.broadcast)}",
                    "total_ips": len(existing_network)
                })

            # Calculate total IPs in the CIDR and existing CIDRs
            total_ips_in_existing_cidrs = sum(len(IPNetwork(existing_cidr)) for existing_cidr in convert_to_list(existing_cidrs))
            
            # Calculate the smallest subnet size
            smallest_subnet = smallest_subnet_size(required_ips)

            # Iterate all_ips and find suitable_range based on the required number of ip addresses
            suitable_range = None
            start_ip = None
            end_ip = None
            suitable_ips = 0

            # Continue the loop until the smallest size is found
            while suitable_range is None:
                for ip in all_ips.iter_cidrs():
                    subnet = IPNetwork(ip)
                    subnet_size = len(subnet)
                    print("Suggested subnet: " + str(subnet.cidr) + " with size: " + str(subnet_size) + " smallest_subnet: " + str(smallest_subnet) + " required_ips: " + str(required_ips) + " total_ips_in_existing_cidrs: " + str(total_ips_in_existing_cidrs) + " total_ips_in_cidr: " + str(total_ips_in_cidr) )
                    if subnet_size < required_ips:
                        print("subnet_size larger than required_ips")
                        continue
                    # If the subnet size is smaller than the required IPs and the smallest subnet size, then it try with the smallest subnet size
                    if subnet.prefixlen >= smallest_subnet and subnet_size >= required_ips:
                        suitable_range = str(subnet.cidr)
                        start_ip = str(subnet.network)
                        end_ip = str(subnet.broadcast)
                        suitable_ips = subnet_size
                        break
                    else:
                        print("Check smallest subnet: " + str(IPNetwork(f"{subnet.ip}/{smallest_subnet}")))
                        subnet = IPNetwork(f"{subnet.ip}/{smallest_subnet}")
                        subnet_size = len(subnet)                   
                        if all_ips.issuperset(IPNetwork(f"{subnet.ip}/{smallest_subnet}")): # is checking if the all_ips IP set includes all the IP addresses in the subnet.
                            suitable_range = str(subnet.cidr)
                            print("suitable_range: " + str(suitable_range))
                            start_ip = str(subnet.network)
                            end_ip = str(subnet.broadcast)
                            suitable_ips = subnet_size
                            break
                # If suitable_range is still None after the loop, decrease the smallest_subnet by 1
                if suitable_range is None:
                    smallest_subnet -= 1
                    # If smallest_subnet is less than 0, break the loop to avoid an infinite loop
                    if smallest_subnet < 0:
                        break          
            
        else:
            print("There are no existing Subnet Ranges")            
            # Find the smallest suitable subnet
            existing_cidrs_info = []
            suitable_range = None
            start_ip = None
            end_ip = None
            suitable_ips = 0
            for prefixlen in range(30, 15, -1):  # Start from /30 and go up to /16
                subnet_size = 2 ** (32 - prefixlen)
                print("prefixLen: " + str(prefixlen))
                print("subnet_size: " + str(subnet_size ))
                if subnet_size < required_ips:
                    print("subnet_size smaller than required_ips")
                    continue
                print("prefixlen provides sufficient requested ip addresses")
                for ip in all_ips.iter_cidrs():
                    print("Check available ip_range: " + str(ip))
                    subnet = IPNetwork(f"{ip.ip}/{prefixlen}")
                    print("subnet: " + str(subnet.cidr))
                    if all_ips.issuperset(subnet): # is checking if the all_ips IP set includes all the IP addresses in the subnet.
                        suitable_range = str(subnet.cidr)
                        print("suitable_range: " + str(suitable_range))
                        start_ip = str(subnet.network)
                        end_ip = str(subnet.broadcast)
                        suitable_ips = subnet_size
                        break
                if suitable_range is not None:
                    break
        
        # Check if the required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR
        if required_ips + total_ips_in_existing_cidrs > total_ips_in_cidr:
            if not json_output:
                return render_template('error.html', error_message='The required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR')
            else:
                errordata = {
                    "error": "input_error",
                    "message": "The required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR",
                    "detail": "Ensure that the number of required IPs plus the IPs in the existing CIDRs are less than the total IPs in the CIDR"
                }
                return jsonify(errordata), 422  
        
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

        if json_output:
            return jsonify(data), 200
        else:    
            # Convert the dictionary to HTML tables
            azure_vnet_ip_range_html, existing_subnets_html, suitable_ip_range_html = json_to_html_table(data)

            print(azure_vnet_ip_range_html)
            print(existing_subnets_html)
            print(suitable_ip_range_html)
            
            return render_template('result.html', azure_vnet_ip_range=azure_vnet_ip_range_html, existing_subnets=existing_subnets_html, suitable_ip_range=suitable_ip_range_html)

    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)