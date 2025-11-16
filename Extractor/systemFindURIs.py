from rapidfuzz import fuzz, process
def findMS(systemPath):
    microservices = []
    rootpath = systemPath.split("Source")[0]
    exclude_path = os.path.join(rootpath, "exclude.txt")

    try:
        with open(exclude_path, 'r') as exclude_file:
            excluded_services = exclude_file.read().split()
    except FileNotFoundError:
        excluded_services = []

    root = os.path.normpath(systemPath)
    root_depth = len(root.split(os.path.sep))

    for dirpath, dirnames, filenames in os.walk(root):
        norm_path = os.path.normpath(dirpath)

        if os.path.sep + "java" + os.path.sep in norm_path:
            java_files = [f for f in filenames if f.endswith(".java")]
            if java_files:
                path_parts = norm_path.split(os.path.sep)
                if len(path_parts) > root_depth:
                    service_name = path_parts[root_depth]
                    if service_name not in excluded_services and service_name not in microservices:
                        print(f"Valid microservice found: {service_name}")
                        microservices.append(service_name)

    return microservices
##########################################################################################################
import glob


def getjavasourcefiles(service_path):
    source_files = []
    fileslist = glob.glob(service_path + "/**/*.java", recursive=True)
    for f in fileslist:
        if "test" not in f.lower():
            source_files.append(f)
    return source_files
###########################################################################################################

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
    class_paths = []
    checkPathclass = ""
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
#######################################################
def save_metadata_to_json(metadata, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
###############################################################
import os
import re

def findCaller2(project_root_path, microservices, selectedservice, strmatch_uri_patterns, javaFilePath):
    relations = []
    reduced_relations = []
    unique_pairs = set()

    rest_template_pattern = re.compile(r'restTemplate\.(get|post|put|delete)For(Object|Entity)\s*\(\s*"([^"]+)"')
    webclient_pattern = re.compile(r'\.uri\(\s*"([^"]+)"')
    uri_patterns = [rest_template_pattern, webclient_pattern]

    for service in microservices:
        if service == selectedservice:
            continue

        micropath = os.path.join(project_root_path, service)
        source_files = getjavasourcefiles(micropath)

        for sf in source_files:

            try:
                with open(sf, "r", encoding="utf-8") as f:
                    content = f.read()
                    found = False
                    for pattern in uri_patterns:
                        for match in pattern.finditer(content):
                            uri = match.group(1) if pattern != rest_template_pattern else match.group(3)
                            for strmatch_uri in strmatch_uri_patterns:
                                if strmatch_uri in uri:
                                    relations.append({
                                        "caller": service,
                                        "caller file": sf,
                                        "matched uri": uri,
                                        "callee": selectedservice,
                                        "callee file": javaFilePath
                                    })
                                    reduced_relations.append({
                                        "caller": service,
                                        "callee": selectedservice
                                    })
                                    found = True
                                    break
                            if found:
                                break

            except Exception as e:
                print(f"Could not read file {sf}: {e}")

    filtered_relations = []
    for rel in reduced_relations:
        pair = (rel["caller"], rel["callee"])
        if pair not in unique_pairs:
            unique_pairs.add(pair)
            filtered_relations.append(rel)

    return relations, filtered_relations

def findCaller(project_root_path, microservices, selectedservice, strmatching, JavaFile, excluded_ms):
    relations = []
    reduced_relations = []
    keyMap =["GetMapping" ,"PostMapping", "PutMapping", "DeleteMapping", "PatchMapping", "RequestMapping"]
    print(JavaFile)
    unique_pairs = set()
    filtered_relations = []

    for service in microservices:

        if service == selectedservice or service in excluded_ms:
            continue
        micropath = os.path.join(project_root_path, service)
        source_files = getjavasourcefiles(micropath)

        for sf in source_files:
            try:
                with open(sf, "r") as f:

                    found = False
                    raw_content = f.read()

                    raw_content = re.sub(r'/\*\*.*?\*/', '', raw_content, flags=re.DOTALL)
                    raw_content = re.sub(r'/\*.*?\*/', '', raw_content, flags=re.DOTALL)

                    raw_content = re.sub(r'//.*', '', raw_content)

                    content = raw_content.splitlines()

                    for line in content:
                        line = line.strip()
                        if not line:
                            continue
                        if strmatching in line and not any(key in line for key in keyMap):

                            relations.append({
                                "caller": service,
                                "caller file": sf,
                                "matched uri": strmatching,
                                "callee": selectedservice,
                                "callee file": JavaFile

                            })
                            reduced_relations.append({
                                "caller": service,
                                "callee": selectedservice
                            })
                            found = True
                            break

            except Exception as e:
                print(f"Could not read file {sf}: {e}")

            filtered_relations = []
            for rel in reduced_relations:
                pair = (rel["caller"], rel["callee"])
                if pair not in unique_pairs:
                    unique_pairs.add(pair)
                    filtered_relations.append(rel)

    return relations, filtered_relations


def findingUniques(reducedRelations):
    filtered_relations = []
    unique_pairs = set()

    for rel in reducedRelations:
        pair = (rel["caller"], rel["callee"])
        if pair not in unique_pairs:
            unique_pairs.add(pair)
            filtered_relations.append(rel)

    return filtered_relations


############################################

import json


def systemFindURIs(proj, results_dir):
    system_data = []
    relations = []
    reducedRelations = []
    microservices = findMS(proj)
    excluded_ms = []
    for service in microservices:
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
    for ms_data in system_data:

        filtered_files = []
        for file_data in ms_data["files"]:
            if file_data.get("caller") or file_data.get("callee") or file_data.get("requestParam"):
                filtered_files.append(file_data)
        ms_data["files"] = filtered_files

    for sn in system_data:
        print(f'service name : {sn["service name"]}')
        has_caller_and_callee = any(
            f.get("caller") and any(c is not None for c in f.get("callee", []))
            for f in sn["files"]
        )

        if not has_caller_and_callee:
            selectedservice = sn["service name"]
            for f in sn["files"]:

                print(f["name"])
                for req in f.get("requestParam", []):
                    method_type = req.get("method_type")
                    uri = req.get("uri")
                    if "/{" in uri:
                        index = uri.index("/{")
                        uri = uri[:index]

                    strmatching = (req.get("@RequestMapping") or "") + (uri  or "")
                    if strmatching and strmatching.strip() not in['', '"', "'", '""', "''", '=', '"=', "'="] and strmatching != "/":
                        if not strmatching.startswith('/') and req.get("uri") == "":
                            strmatching += '/'
                            print(f'strmatching for findCaller :{strmatching}')
                        relat, reducedRel = findCaller(proj, microservices, selectedservice, strmatching,
                                                       f["name"],
                                                       excluded_ms)

                        if relat:
                            for r in relat:
                                service_relation = {
                                    "caller": r.get("caller"),
                                    "caller file": r.get("caller file"),
                                    "matched uri": r.get("matched uri"),
                                    "callee": r.get("callee"),
                                    "callee file": r.get("callee file"),
                                    "callee method type": method_type#,

                                }

                                relations.append(service_relation)
    for cc in system_data:
        for f in cc["files"]:
            if f.get("caller") and f["callee"] != [None]:
                callee_list = f.get("callee")

                if callee_list and microservices:
                    for callee in callee_list:


                        result = process.extractOne(callee, microservices, scorer=fuzz.token_sort_ratio)
                        if result:
                            best_match, score, _ = result

                            case = ""
                            if best_match != f.get("caller"):
                                case = best_match
                            else:
                                case = callee
                            service_relation = {
                                "caller": f.get("caller"),
                                "caller file": f.get("name"),
                                "mached uri": "",
                                "callee": case,
                                "callee file": "",
                                "callee method type": "feign client"
                            }
                            relations.append(service_relation)


    reducedrelations = findingUniques(relations)

    def remove_duplicates_dict_list(dict_list):
        seen = set()
        unique_list = []
        for d in dict_list:
            items_tuple = tuple(sorted(d.items()))
            if items_tuple not in seen:
                seen.add(items_tuple)
                unique_list.append(d)
        return unique_list


    relations = remove_duplicates_dict_list(relations)
    reducedrelations = remove_duplicates_dict_list(reducedrelations)

    return relations, reducedrelations


