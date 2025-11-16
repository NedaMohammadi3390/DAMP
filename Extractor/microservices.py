import os
import re

import os

def extract(root):
    microservices = []
    print(f"Root path: {root}")
    rootpath = root.split("Source")[0]
    exclude_path = os.path.join(rootpath, "exclude.txt")

    try:
        with open(exclude_path, 'r') as exclude_file:
            excluded_services = exclude_file.read().split()
    except FileNotFoundError:
        print(f"Warning: {exclude_path} not found. No services will be excluded.")
        excluded_services = []

    root = os.path.normpath(root)
    root_depth = len(root.split(os.path.sep))

    for dirpath, dirnames, filenames in os.walk(root):
        norm_path = os.path.normpath(dirpath)
        path_parts = norm_path.split(os.path.sep)


        if len(path_parts) > root_depth:
            service_name = path_parts[root_depth]

            service_path = os.path.join(root, service_name)

            src_path = os.path.join(service_path, "src")

            if (
                    service_name not in excluded_services
                    and service_name not in microservices
                    and os.path.isdir(src_path)
            ):
                print(f"✅ Valid microservice found: {service_name} (contains 'src')")
                microservices.append(service_name)

    return microservices

##########################################################
##########################################################
##########################################################
def getlang(service):

    enry_path = os.path.expanduser("~/go/bin/enry")
    command = f"{enry_path} {service}"
    toplang = os.popen(command).read()

    if toplang:

        result = toplang.split("%")[1].split()[0].lower().strip()
        percentage = toplang.split("%")[0].strip()
        print("Top Language:", result)
        return result, percentage
    else:
        return "unknown", "0"
##########################################################
##########################################################
##########################################################
def getlocs(service):
    cloc = os.popen("cloc " + service)
    output = cloc.read()

    values = [1, 1, 1, 1]

    if "-----" in output:
        lines = output.splitlines()

        for line in lines:
            if line.startswith("SUM"):
                values = re.findall(r'\d+', line)
    return values
