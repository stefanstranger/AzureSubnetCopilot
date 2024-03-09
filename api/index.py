from flask import Flask, request, jsonify, render_template
from netaddr import IPNetwork, IPSet

app = Flask(__name__)

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
        existing_cidrs = request.form["subnet_ipranges"]
        required_ips = int(request.form["required_ips"])       

        all_ips = IPSet(IPNetwork(cidr))
        existing_cidrs_info = []
        for existing_cidr in convert_to_list(existing_cidrs):
            existing_network = IPNetwork(existing_cidr)
            all_ips.remove(existing_network)
            existing_cidrs_info.append({
                "cidr": existing_cidr,
                "start_end_ip": f"{str(existing_network.network)} - {str(existing_network.broadcast)}",
                "total_ips": len(existing_network)
            })
        # Calculate total IPs in the CIDR and existing CIDRs
        total_ips_in_cidr = len(IPNetwork(cidr))
        total_ips_in_existing_cidrs = sum(len(IPNetwork(existing_cidr)) for existing_cidr in convert_to_list(existing_cidrs))

        # Check if the required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR
        if required_ips + total_ips_in_existing_cidrs > total_ips_in_cidr:
            return jsonify({"error": "The required IPs plus the IPs in the existing CIDRs exceed the total IPs in the CIDR"})
    
        # Find the smallest suitable subnet
        suitable_range = None
        start_ip = None
        end_ip = None
        suitable_ips = 0
        for prefixlen in range(30, 16, -1):  # Start from /30 and go up to /17
            subnet_size = 2 ** (32 - prefixlen)
            if subnet_size < required_ips:
                continue
            for ip in all_ips.iter_cidrs():
                subnet = IPNetwork(f"{ip.ip}/{prefixlen}")
                if all_ips.issuperset(subnet):
                    suitable_range = str(subnet.cidr)
                    start_ip = str(subnet.network)
                    end_ip = str(subnet.broadcast)
                    suitable_ips = subnet_size
                    break
            if suitable_range is not None:
                break
    
        ip_ranges = {
            "cidr": cidr,
            "start_end_ip": f"{str(IPNetwork(cidr).network)} - {str(IPNetwork(cidr).broadcast)}",
            "total_ips": len(IPNetwork(cidr))
        }
    
        return jsonify({"ip_ranges": ip_ranges, "existing_cidrs": existing_cidrs_info, "start_end_ip": f"{start_ip} - {end_ip}", "suitable_range": suitable_range, "total_ips": suitable_ips})
        
    return render_template("home.html")

#if __name__ == '__main__':
#    app.run(debug=True)
