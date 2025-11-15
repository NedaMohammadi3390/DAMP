import glob
import os

def getjavasourcefiles(service_path):
    source_files = []
    fileslist = glob.glob(service_path + "/**/*.java", recursive=True)
    for f in fileslist:
        if "test" not in f.lower():
            source_files.append(f)
    return source_files


###########################################################################################################
import re
def find_feignClient(java_path, service_name):
    feign_relations = []

    feign_pattern = re.compile(
        r'@(?P<annotation>(FeignClient))\s*(\((?P<params>.*?)\))?',
        re.DOTALL
    )
    with open(java_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matchFeignlist = list(re.finditer(feign_pattern, content))

    if matchFeignlist:
        for match in matchFeignlist:
            feign_params = match.group('params') or ""

            name_match = re.search(r'(name|value)\s*=\s*"([^"]+)"', feign_params)
            if name_match:

                feign_name = name_match.group(2)
                feign_params = feign_name.strip('"\'')
                feign_relations.append(feign_params)

            elif feign_params and not name_match:
                feign_params = feign_params.strip('"\'')
                feign_relations.append(feign_params)

    return feign_relations
###########################################################################################
def find_RequestParam_uri(java_path):
    global class_base_path
    mappings = []
    import re

    api_endpoints = []
    class_request_mapping_pattern = re.compile(
        r'@(?P<annotation>(RequestMapping))\s*(\((?P<params>.*?)\))?',
        re.DOTALL
    )

    method_signature_pattern = re.compile(r'(?:public|protected|private)?\s*[\w<>\[\]]+\s+(\w+)\s*\(', re.MULTILINE)

    with open(java_path, 'r', encoding='utf-8') as f:
        content = f.read()

    class_base_path = ""
    hasclass = False
    pattern = r'(value|path)\s*=\s*"(?P<uri>.*?)"\s*,\s*method\s*=\s*RequestMethod\.(?P<method>\w+)'

    mappingsClassMethods = list(re.finditer(class_request_mapping_pattern, content))
    if mappingsClassMethods:
        for match in mappingsClassMethods:
            start_index = match.end()

            following_code = content[start_index:min(start_index + 300, len(content))]

            if re.search(r'\b(public\s+)?(class|interface)\s+\w+', following_code):
                hasclass = True
                potentialClassInterface = match.group(0)
                checkPathclass = re.search(pattern, potentialClassInterface)
                if not checkPathclass:
                    class_base_path_general = match.group('params')
                    decision = re.search(r'(value|path)\s*=\s*"(?P<uri>[^"]+)"', class_base_path_general)

                    if decision and decision.group('uri'):
                        class_base_path = decision.group('uri')
                        class_base_path = class_base_path.strip('"\'')
                    else:
                        class_base_path = class_base_path_general
                        class_base_path = class_base_path.strip('"\'')
    if mappingsClassMethods and len(mappingsClassMethods) > 1:
        method_mapping_pattern = re.compile(
            r'@(?P<annotation>(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping))\s*(\((?P<params>.*?)\))?',
            re.DOTALL
        )
        mappings = list(re.finditer(method_mapping_pattern, content))
        if hasclass:
            del mappings[0]

    else:
        method_mapping_pattern = re.compile(
            r'@(?P<annotation>(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping))\s*(\((?P<params>.*?)\))?',
            re.DOTALL
        )
        mappings = list(re.finditer(method_mapping_pattern, content))

    for match in mappings:
        annotation = match.group('annotation')
        params = match.group('params') or ""
        flagvalue = re.search(r'(value|path)\s*=\s*"(?P<uri>.*?)"\s*', params)
        if flagvalue != None:
            flagvalue = flagvalue.group('uri')
            params = flagvalue.strip('"\'')

        method_type = "-"
        uri = ""
        if '""' in uri:
            uri = uri.strip('"\'')

        if annotation == "GetMapping":
            method_type = "GET"
        elif annotation == "PostMapping":
            method_type = "POST"
        elif annotation == "PutMapping":
            method_type = "PUT"
        elif annotation == "DeleteMapping":
            method_type = "DELETE"
        elif annotation == "PatchMapping":
            method_type = "PATCH"
        elif annotation == "RequestMapping":
            method_match = re.search(r'method\s*=\s*RequestMethod\.(\w+)', params)
            if method_match:
                method_type = method_match.group(1)

        uri_match = re.search(r'(?:path|value)?\s*=\s*["\'](.+?)["\']|["\'](.+?)["\']', params)

        if params and uri_match:
            uri = uri_match.group(2)
        elif params and not uri_match:
            uri = params

        remaining_content = content[match.end():]
        method_match = method_signature_pattern.search(remaining_content)
        method_name = method_match.group(1) if method_match else "-"

        api_endpoints.append({
            "method": method_type,
            "@RequestMapping": class_base_path,
            "uri": uri,
            "method_name": method_name
        })

    return api_endpoints

###############################################################

def findUri(proj, service, results_dir):

    system_data = []
    excluded_ms = []
    ms_data = {}
    micropath = os.path.join(proj, service)
    source_files = getjavasourcefiles(micropath)
    ms_data["service name"] = service

    ms_data["files"] = []

    for sf in source_files:
        file_data = {
            "name": sf,
            "caller": "",
            "callee": "",
            "requestParam": []
        }

        callee = find_feignClient(sf, service)
        if callee and callee[0] != None:
            file_data["caller"] = service
            file_data["callee"] = callee
            excluded_ms.append(service)

        api_endpoints = find_RequestParam_uri(sf)
        if api_endpoints:
            for ae in api_endpoints:
                file_data["requestParam"].append({
                    "method_type": ae.get("method"),
                    "@RequestMapping": ae.get("@RequestMapping"),
                    "uri": ae.get("uri"),
                    "method_name": ae.get("method_name")
                })

        ms_data["files"].append(file_data)

    system_data.append(ms_data)

    return system_data