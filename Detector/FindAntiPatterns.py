from collections import defaultdict
import yaml
import math

vars = dict()

# خواندن فایل کانفیگ
with open("thresholds_config.yaml", "r") as f:
    config = yaml.safe_load(f)

def generalInformation(metamodel, apd_Detected ):
    apd_Detected['GeneralInformation'] = {
        'number of services': 0,
        'total LOCs': 0,
        'total files': 0,
        'average LOCs': 0,
        'average files': 0,
        'number of apis':0,
        'serviceName':[]
    }
    apd_Detected['GeneralInformation']['number of services'] = apd_Detected['GeneralInformation'].setdefault("number of services", 0) +\
                                                               len(metamodel["system"]["microservices"])

    apd_Detected['GeneralInformation']['total LOCs'] = apd_Detected['GeneralInformation'].setdefault("total LOCs", 0)

    apd_Detected['GeneralInformation']['total files'] = apd_Detected['GeneralInformation'].setdefault("total files", 0)

    for service in metamodel["system"]["microservices"]:
        apd_Detected['GeneralInformation']['serviceName'].append(service["name"])
        apd_Detected['GeneralInformation']['total LOCs'] = apd_Detected['GeneralInformation']['total LOCs'] + int(service["locs"])
        apd_Detected['GeneralInformation']['total files'] = apd_Detected['GeneralInformation']['total files'] + int(service["nb_files"])
        apd_Detected['GeneralInformation']['number of apis'] = apd_Detected['GeneralInformation']['number of apis'] + int(service["code"]["APIs"]["number"])
    apd_Detected['GeneralInformation']['average LOCs'] = apd_Detected['GeneralInformation'].setdefault("average LOCs", 0) + \
                                                         (apd_Detected['GeneralInformation']['total LOCs'] /
                                                          apd_Detected['GeneralInformation']['number of services'])
    apd_Detected['GeneralInformation']['average files'] = apd_Detected['GeneralInformation'].setdefault("average files", 0) + (
            apd_Detected['GeneralInformation']['total files'] / apd_Detected['GeneralInformation']['number of services'])

    vars["number of services"] = apd_Detected['GeneralInformation']['number of services']
    vars["total LOCs"] = apd_Detected['GeneralInformation']['total LOCs']
    vars["total files"] = apd_Detected['GeneralInformation']['total files']
    vars["average LOCs"] = apd_Detected['GeneralInformation']['average LOCs']
    vars["average files"] = apd_Detected['GeneralInformation']['average files']
    vars['number of apis'] = apd_Detected['GeneralInformation']['number of apis']
    return apd_Detected

############################################################
#                     antipattern 1: hasWrongCuts
#############################################################
def WrongCuts(metamodel, apd_Detected):
    flag_folders = []
    apd_Detected['WrongCuts'] = {
        'hasWrongCuts': False,
        'services': []
    }

    with open("../tools/config_extensions.txt", "r") as confTools:
        tools_extension = [line.strip() for line in confTools]

    with open("../tools/web_extensions.txt", "r") as webTools:
        tools_web = [line.strip() for line in webTools]

    microservices = metamodel["system"]["microservices"]

    web_ratio = config["wrongcuts_thresholds"]["web_ratio"]
    for service in microservices:
        sFiles = service["code"]["source_files"]
        number_files = len(sFiles)
        extension_counts = {}
        cpt = 0

        for sf in sFiles:
            if "." in sf:
                extension = sf.split(".")[1]
                extension_counts[extension] = extension_counts.get(extension, 0) + 1

        for ext, count in extension_counts.items():
            if ext in tools_extension:
                number_files -= count
            if ext in tools_web:
                cpt += count


        if cpt > config["wrongcuts_thresholds"]["min_count"] and cpt >= number_files * web_ratio and service["name"] not in flag_folders:
            flag_folders.append(service["name"])
            apd_Detected['WrongCuts']['hasWrongCuts'] = True
            apd_Detected['WrongCuts']['services'].append({
                'name': service["name"],
                'type': 'Web',
                'countdataModel': cpt,
                'totalnumber_files': number_files
            })

    with open("../tools/wrongcuts_annotations.txt", "r") as annota:
        tools_annotations = [line.strip() for line in annota]

    for service in microservices:
        sFiles = service["code"]["source_files"]
        number_files = len(sFiles)
        countdataModel = 0
        datamodel = {}
        annotations = service["code"]["annotations"]
        declared_annotations = service["code"]["declared_annotations"]

        for tan in tools_annotations:
            for annot_ser in annotations:
                if annot_ser:
                    annot_ser = annot_ser.split("/")[-1]
                    if tan == annot_ser:
                        countdataModel += 1
                        datamodel[tan] = datamodel.get(tan, 0) + 1

            for dec_anno in declared_annotations:
                if dec_anno and tan == dec_anno:
                    countdataModel += 1
                    datamodel[tan] = datamodel.get(tan, 0) + 1

        if countdataModel > 1 and countdataModel >= len(annotations + declared_annotations) * 0.6 and service[
            "name"] not in flag_folders:
            flag_folders.append(service["name"])
            apd_Detected['WrongCuts']['hasWrongCuts'] = True
            apd_Detected['WrongCuts']['services'].append({
                'name': service["name"],
                'type': 'Datamodel',
                'countdataModel': countdataModel,
                'totalnumber_files': number_files
            })

    # ------------------------
    with open("../tools/logic_annotations.txt", "r") as logicFile:
        tools_logic = [line.strip() for line in logicFile]

    for service in microservices:
        annotations = service["code"]["annotations"]
        declared_annotations = service["code"]["declared_annotations"]
        logic_count = 0
        model_count = 0
        ui_file_count = 0

        total_annots = annotations + declared_annotations

        for ann in total_annots:
            ann = ann.split("/")[-1]
            if ann in tools_logic:
                logic_count += 1
            if ann in tools_annotations:
                model_count += 1

        for sf in service["code"]["source_files"]:
            if "." in sf:
                extension = sf.split(".")[1]
                if extension in tools_web:
                    ui_file_count += 1

        total_ann_count = len(total_annots)
        if total_ann_count > 0:
            logic_ratio = logic_count / total_ann_count
            if logic_ratio > 0.8 and model_count == 0 and ui_file_count == 0 and service["name"] not in flag_folders:
                flag_folders.append(service["name"])
                apd_Detected['WrongCuts']['hasWrongCuts'] = True
                apd_Detected['WrongCuts']['services'].append({
                    'name': service["name"],
                    'type': 'Logic',
                    'count_logic': logic_count,
                    'total_annotations': total_ann_count
                })
    return apd_Detected

############################################################
#                     antipattern 2: MegaService
#############################################################
def megaService(metamodel, apd_Detected):
    apd_Detected['megaService'] = {
        'hasMegaService': False,
        'characteristics of mega services': []
    }
    thresholds = config["megaService_thresholds"]
    totalAPI = 0
    apiServices = []

    for s in metamodel["system"]["microservices"]:
        name = s['name']
        num_api = s["code"]["APIs"]["number"]
        apiServices.append({
            'service name': name,
            'number api': num_api,
            'locs': s["locs"],
            'nbFiles': s["nb_files"]
        })
        totalAPI += num_api

    mega_services = []

    for s in apiServices:
        name = s['service name']
        locs = int(s['locs'])
        files = s['nbFiles']
        num_api = s['number api']

        requiredLocs = vars["total LOCs"] * thresholds["loc_ratio"]
        hasMoreLocsThanAvg = locs > requiredLocs
        isNotDemoOrCommand = "demo" not in name.lower() and "command" not in name.lower()
        api_ratio = num_api / totalAPI if totalAPI > 0 else 0

        if hasMoreLocsThanAvg and isNotDemoOrCommand and api_ratio > thresholds["api_ratio"]:
            apd_Detected['megaService']['hasMegaService'] = True
            mega_services.append({
                'service name': name,
                'locs': locs,
                'nbFiles': files,
                'requiredLocs': requiredLocs,
                "total LOCs in system": vars["total LOCs"],
                "average LOCs in system": vars["average LOCs"],
                'api_ratio': api_ratio,
                'the number api in MS': num_api,
                'total number api in system': totalAPI
            })

    apd_Detected['megaService']['characteristics of mega services'] = mega_services
    return apd_Detected

############################################################
#                     antipattern 3: NanoService
#############################################################
import math

def nanoService(metamodel, apd_Detected):
    apd_Detected['nanoService'] = {
        'hasNanoService': False,
        'characteristics of nano services': []
    }

    thresholds = config["nanoService_thresholds"]
    totalAPI = 0
    for s in metamodel["system"]["microservices"]:
        totalAPI += s["code"]["APIs"]["number"]

    with open("../tools/name_ban_for_nano_services.txt", "r") as confTools:
        tools = [line.strip() for line in confTools if line.strip()]


    requiredLocs = math.floor(thresholds["loc_ratio"] * vars["average LOCs"])
    requiredFiles = math.floor(thresholds["files_ratio"] * vars["average files"])

    for s in metamodel["system"]["microservices"]:
        name = s['name']
        num_api = s["code"]["APIs"]["number"]

        red_flag_service_name = any(tool_name in name for tool_name in tools)

        hasLessLocsThanAvg = int(s["locs"]) < requiredLocs
        hasLessFilesThanAvg = int(s["nb_files"]) < requiredFiles
        ratio = num_api / totalAPI if totalAPI > 0 else 0

        if (hasLessLocsThanAvg  and ratio <= thresholds["api_ratio"] and not red_flag_service_name):
            apd_Detected['nanoService']['hasNanoService'] = True
            apd_Detected['nanoService']["characteristics of nano services"].append({
                "service name": name,
                "locs": s["locs"],
                "nbFiles": s["nb_files"],
                "requiredLocs": requiredLocs,
                "requiredFiles": requiredFiles,
                "total LOCs in system": vars["total LOCs"],
                "average LOCs in system": vars["average LOCs"],
                "api_ratio": ratio,
                "number api in service": num_api,
                "total number api in system": totalAPI
            })

    return apd_Detected


############################################################
#                     antipattern 4: SharedDependencies
#############################################################

def sharedDependencies(metamodel, apd_Detected):
    apd_Detected['sharedDependencies'] = {
        "hasSharedDependency": False,
        "dependency in config file": [],
        "dependency in imported section": [],
        "sharedLibrariesWithFilePath": {}
    }

    sharedLibrariesWithFilePath = {}
    sharedLibraries = defaultdict(set)
    dictDepService = defaultdict(set)

    # نام تمامی میکروسرویس ها را از فایل metamodel میخوانم.
    services = metamodel["system"]["candidateMicroservices"]

    with open("../tools/not_shared_dependencies.txt", "r") as confTools:
        tools = [line.strip() for line in confTools.readlines()]

    for s in metamodel["system"]["microservices"]:
        name = s["name"]
        deps = s["dependencies"]

        for dep in deps:
            if dep not in tools:

                dictDepService[dep].add(name)

        sName = s["name"]
        imports_raw = s["code"]["imports"]

        import_names = [entry.split('/')[-1] for entry in imports_raw]
        file_paths = [entry.rsplit('/', 1)[0] for entry in imports_raw]

        unique_imports = set()


        for idx, imp in enumerate(import_names):
            imp_lower = imp.lower()
            for mserv in services:
                mservDot = mserv.replace('-', '.').replace('_', '.').lower()
                sName_lower = sName.lower()
                if sName_lower == mserv:
                    continue

                if f".{mservDot}." in imp_lower or imp_lower.endswith(f".{mservDot}"):
                    unique_imports.add((mserv, file_paths[idx]))
                    sharedLibraries[sName].add(imp_lower)

        if unique_imports:
            sharedLibrariesWithFilePath[sName] = [
                {
                    'service imported': serv,
                    'file path': path
                } for serv, path in unique_imports
            ]

    apd_Detected['sharedDependencies']["sharedLibrariesWithFilePath"] = sharedLibrariesWithFilePath
    apd_Detected['sharedDependencies']["dependency in imported section"] = {
        k: sorted(list(v)) for k, v in sharedLibraries.items()
    }

    for dep, servs in dictDepService.items():
        if len(servs) > 1:
            apd_Detected['sharedDependencies']["hasSharedDependency"] = True
            apd_Detected['sharedDependencies']["dependency in config file"].append({
                "dependency": dep,
                "services": sorted(list(servs))
            })

    return apd_Detected
############################################################
#                     antipattern 5: HardcodedEndpoints
#############################################################

# Rule : intersect(Service discovery, dependencies) = 0 AND (count(URLs, source code) > 0 OR count(URLs, config files) > 0)
def hardcodedEndpoints(metamodel, apd_Detected):

    apd_Detected["hardcodedEndpoints"] = {
        "hashardcodedEndpoints": False,
        "hasServiceDiscoveryTools": False,
        "system": {
            "ServiceDiscoveryTool": [],
            "FoundUrls": [],
            "UrlPath": []
        },
        "service": []
    }
    hardcodedEndpoints = {}

    with open("../tools/service_discovery.txt", "r") as sdTools:
        tools = [line.strip() for line in sdTools if line.strip()]

    for service in metamodel["system"]["microservices"]:
        res = []

        for dependency in service.get("dependencies", []):
            for tool in tools:
                if tool in dependency:
                    apd_Detected["hardcodedEndpoints"]["hasServiceDiscoveryTools"] = True
                    if tool not in res:
                        res.append(tool)


        http_urls = service["code"].get("http", [])
        if any(http_url.get("url") for http_url in http_urls):
            apd_Detected["hardcodedEndpoints"]["hashardcodedEndpoints"] = True

        for http_url in http_urls:
            found_url = http_url.get("url")
            found_path = http_url.get("url path")
            if found_url or res:
                apd_Detected["hardcodedEndpoints"]["service"].append({
                    "service name": service.get("name", "UNKNOWN"),
                    "ServiceDiscoveryTool": res,
                    "FoundUrls": [found_url] if found_url else [],
                    "UrlPath": [found_path] if found_path else []
                })

        if http_urls:
            hardcodedEndpoints[service.get("name", "UNKNOWN")] = {
                "hasServiceDiscoveryTool": len(res) > 0,
                "FoundUrls": ", ".join(http_url.get("url", "") for http_url in http_urls if http_url.get("url path"))
            }

    sysres = []
    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency and tool not in sysres:
                apd_Detected["hardcodedEndpoints"]["system"]["ServiceDiscoveryTool"].append(tool)
                sysres.append(tool)

    system_http = metamodel["system"].get("http", [])
    for http_url in system_http:
        found_url = http_url.get("url")
        found_path = http_url.get("path")
        if found_url:
            apd_Detected["hardcodedEndpoints"]["system"]["FoundUrls"].append(found_url)
        if found_path:
            apd_Detected["hardcodedEndpoints"]["system"]["UrlPath"].append(found_path)

    if system_http:
        hardcodedEndpoints["system"] = {
            "hasServiceDiscoveryTool": len(sysres) > 0,
            "FoundUrls": ", ".join(http_url.get("url", "") for http_url in system_http if http_url.get("url path"))
        }

    if hardcodedEndpoints:
        apd_Detected["hardcodedEndpoints"]["hashardcodedEndpoints"] = True

    return apd_Detected

############################################################
#                     antipattern 6: ManualConfiguration
#############################################################
def manualConfiguration(metamodel, apd_Detected):
    apd_Detected["manualConfiguration"] = {
        "system": {
            "hasConfigurationTool": False,
            "FoundConfigFiles": []
        },
        "service": []
    }

    hasManualConfig = {}

    with open("../tools/configuration.txt", "r") as confTools:
        tools = [line.strip() for line in confTools if line.strip()]

    sysres = []

    for service in metamodel["system"]["microservices"]:
        res = []

        for dependency in service.get("dependencies", []):
            for tool in tools:
                if tool in dependency:
                    res.append(tool)

        if res:
            apd_Detected["manualConfiguration"]["service"].append({
                "service name": service["name"],
                "FoundConfigFiles": res
            })

        config_files = service.get("config", {}).get("config_files", [])
        if config_files:
            hasManualConfig[service["name"]] = {
                "hasConfigurationTool": len(res) > 0,
                "FoundConfigFiles": ", ".join(config_files)
            }

    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency:
                sysres.append(tool)

    if sysres:
        apd_Detected["manualConfiguration"]["system"]["hasConfigurationTool"] = True
        apd_Detected["manualConfiguration"]["system"]["FoundConfigFiles"].extend(sysres)

    return apd_Detected


############################################################
#                     antipattern 7: NO CICD
#############################################################
import fnmatch


def NoCiCd(metamodel, apd_Detected):
    apd_Detected["NoCICD"] = {
        'system': {
            'system level': False,
            "hasCiCdFolders": [],
            "hasConfigCiCD": [],
            'hasDependencyCiCD': [],
            'hasKeywordsCiCD': [],
        },
        'service': {
            'service name': [],
            "hasCiCdFolders": [],
            "hasConfigCiCD": [],
            'hasDependencyCiCD': [],
            'hasKeywordsCiCD': [],
        }
    }

    with open("../tools/cicd_folders.txt") as cicd:
        cifolders = [line.strip() for line in cicd.readlines()]
        for ci in cifolders:
            if ci in metamodel["system"]["folders"]:
                apd_Detected["NoCICD"]['system']['system level'] = True
                apd_Detected["NoCICD"]['system']["hasCiCdFolders"].append(ci)

    with open("../tools/cicd.txt", "r") as sdTools:
        tools = [line.strip() for line in sdTools if line.strip()]

    with open("../tools/cicd_config_file.txt", "r") as conTools:
        cicd_patterns = conTools.read().splitlines()

    with open("../tools/ci_cd_keywords.txt", "r") as keyw:
        keywords = keyw.read().splitlines()

    for service in metamodel["system"]["microservices"]:
        name = service["name"]

        for dependency in service["dependencies"]:
            for tool in tools:
                if tool in dependency:
                    apd_Detected["NoCICD"]['service']['service name'].append(name)
                    apd_Detected["NoCICD"]['service']['hasDependencyCiCD'].append(dependency)

        for conf in service["config"]["config_files"]:
            for cicdpat in cicd_patterns:
                if fnmatch.fnmatch(conf, f"*{cicdpat}"):
                    if ".github/workflows/*.yml" in cicdpat:
                        with open(conf, "r", encoding="utf-8", errors="ignore") as cf:
                            content = cf.read()
                        if ("name: CD Pipeline" or "name: Java CI") in content:
                            apd_Detected["NoCICD"]['service']['service name'].append(name)
                            apd_Detected["NoCICD"]['service']["hasConfigCiCD"].append(conf)
                    else:
                        apd_Detected["NoCICD"]['service']['service name'].append(name)
                        apd_Detected["NoCICD"]['service']["hasConfigCiCD"].append(conf)
            try:
                with open(conf, "r", encoding="utf-8", errors="ignore") as cf:
                    content = cf.read()
                    found_keywords = [kw for kw in keywords if kw in content]
                    if found_keywords:
                        apd_Detected["NoCICD"]['service']['service name'].append(name)
                        apd_Detected["NoCICD"]['service']['hasKeywordsCiCD'].append(found_keywords)
            except Exception as e:
                print(f"Error in reading {conf}: {e}")

    for dependency in metamodel["system"]["dependencies"]:
        for tool in tools:
            if tool in dependency:
                apd_Detected["NoCICD"]['system']['system level'] = True
                apd_Detected["NoCICD"]['system']['hasDependencyCiCD'].append(tool)

    for conf in metamodel["system"]["config_files"]:
        for cicdpat in cicd_patterns:
            if fnmatch.fnmatch(conf, f"*{cicdpat}"):

                if ".github/workflows/*.yml" in cicdpat:
                    with open(conf, "r", encoding="utf-8", errors="ignore") as cf:
                        content = cf.read()
                    if ("name: CD Pipeline" or "name: Java CI") in content:
                        apd_Detected["NoCICD"]['system']['system level'] = True
                        apd_Detected["NoCICD"]['service']["hasConfigCiCD"].append(conf)

        try:
            with open(conf, "r", encoding="utf-8", errors="ignore") as cf:
                content = cf.read()
                found_keywords = [kw for kw in keywords if kw in content]
                if found_keywords:
                    apd_Detected["NoCICD"]['system']['system level'] = True
                    apd_Detected["NoCICD"]['system']['hasKeywordsCiCD'].append(found_keywords)
        except Exception as e:
            print(f"Error in reading {conf}: {e}")

    return apd_Detected


############################################################
#                     antipattern 8: ApiGateway
#############################################################

def apiGateway(metamodel, apd_Detected):
    apd_Detected['apiGateway'] = {
        'system': {
            'system level': False,
            'system dependency': []
        },
        'service': []
    }

    with open("../tools/gateway.txt", "r") as sdTools:
        tools = [line.strip() for line in sdTools if line.strip()]

    for service in metamodel["system"]["microservices"]:
        service_gateway_deps = []

        for dependency in service.get("dependencies", []):
            matched_tools = [tool for tool in tools if tool in dependency]
            if matched_tools:
                service_gateway_deps.append(dependency)

        if service_gateway_deps:
            apd_Detected['apiGateway']['service'].append({
                "service name": service["name"],
                "service dependencies": service_gateway_deps
            })

    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency:
                apd_Detected['apiGateway']['system']['system level'] = True
                apd_Detected['apiGateway']['system']['system dependency'].append(dependency)
                break  # مشابه بالا

    return apd_Detected

############################################################
#                     antipattern 9: Timeouts
#############################################################

def Timeouts(metamodel, apd_Detected):

    apd_Detected['Timeouts'] = {
        "flagTO" : None,
        'service': []
    }

    with open("../tools/circuit_breaker.txt", "r") as sdTools:
        tools = [line.strip() for line in sdTools if line.strip()]
    systemFlag = True
    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency:
                systemFlag = False
                break


    if systemFlag:
        # Microservice level
        for service in metamodel["system"]["microservices"]:
            serviceFlag = True
            service_entry = {
                'service name': service['name'],
                'service dependency': set(),
                'hasTOImports': False,
                'ToImports': [],
                'hasFBImports': False,
                'FbImports': [],
                'hasTOMethods': False,
                'ToMethods': [],
                'hasFBMethods': False,
                'FbMethods': []
            }

            for dependency in service.get("dependencies", []):
                for tool in tools:
                    if tool in dependency:
                        serviceFlag = False
                        service_entry['service dependency'].add(dependency)
                        break

            if serviceFlag:
                for imp in service["code"].get("imports", []):
                    imp = imp.split('/')[-1]
                    if "timeout" in imp.lower():
                        service_entry['hasTOImports'] = True
                        service_entry['ToImports'].append(imp)
                    if "fallback" in imp.lower():
                        service_entry['hasFBImports'] = True
                        service_entry['FbImports'].append(imp)

                for meth in service["code"].get("methods", []):
                    meth = meth.split('/')[-1]
                    if "timeout" in meth.lower():
                        service_entry['hasTOMethods'] = True
                        service_entry['ToMethods'].append(meth)
                    if "fallback" in meth.lower():
                        service_entry['hasFBMethods'] = True
                        service_entry['FbMethods'].append(meth)

            if (serviceFlag and
                    (service_entry['hasTOImports'] or
                    service_entry['hasFBImports']
                    # service_entry['hasTOMethods'] or
                    # service_entry['hasFBMethods']
                            )):
                apd_Detected['Timeouts']["flagTO"] = True
                apd_Detected['Timeouts']['service'].append(service_entry)
    return apd_Detected

############################################################
#                     antipattern 10: MultipleServicesPerHost
#############################################################
def MultipleServicesPerHost(metamodel, apd_Detected):
    apd_Detected['MultipleServicesPerHost'] = {
        'system': {
            'hasDockerCompose': False
        },
        'service': []
    }

    for file in metamodel["system"].get("config_files", []):
        if ("docker-compose.yml" or "docker-compose.yaml") in file.lower():
            apd_Detected['MultipleServicesPerHost']['system']['hasDockerCompose'] = True
            break

    for service in metamodel["system"].get("microservices", []):
        has_dockerfile = any("dockerfile" in f.lower() for f in service["code"].get("source_files", []))

        if has_dockerfile:
            apd_Detected['MultipleServicesPerHost']['service'].append({
                'service name': service['name'],
                'hasDockerFile': True
            })

    return apd_Detected


############################################################
#                     antipattern 11: SharedPersistence
#############################################################
def SharedPersistence(metamodel, apd_Detected):
    apd_Detected['SharedPersistence'] = {
        'sharedDatabases': []
    }

    db_to_info = {}

    for service in metamodel["system"]["microservices"]:
        name = service["name"]
        datasources = service.get("code", {}).get("databases", {}).get("datasources", [])

        for ds in datasources:
            db_type = ""
            db_name = ""
            if ':' in ds:
                db_name, db_type = ds.split(":", 1)

            if not db_name or not db_type:
                continue

            key = (db_name, db_type)

            if key not in db_to_info:
                db_to_info[key] = {
                    'services': [name]
                }
            else:
                db_to_info[key]['services'].append(name)

    for (db_name, db_type), info in db_to_info.items():
        if len(info['services']) > 1:
            apd_Detected['SharedPersistence']['sharedDatabases'].append({
                'database': db_name,
                'type': db_type,
                'services': info['services']
            })

    return apd_Detected
############################################################
#                     antipattern 12: ApiVersioning
#############################################################
#
import re

def ApiVersioning(metamodel, apd_Detected):
    apd_Detected['ApiVersioning'] = {
        'servicehasAPIVersioning': False,
        'SystemhasAPIVersioning': False,
        "systemUri": [],
        'system': [],
        'service': []
    }

    for re_item in metamodel['system'].get('relations', []):
        uri = re_item.get("matched uri", "")

        if re.search(r'(^|/)v[1-4](/|$)', uri):
            apd_Detected['ApiVersioning']["servicehasAPIVersioning"] = True
            apd_Detected['ApiVersioning']['SystemhasAPIVersioning'] = True
            apd_Detected['ApiVersioning']["systemUri"].append(uri)

    for service in metamodel["system"].get("folders", []):
        serviceApiVersions = []
        service_uriversion = []
        if isinstance(service, dict):
            if service.get("config", {}).get("config_files", []):

                for conf_file in service.get("config", {}).get("config_files", []):
                    try:
                        with open(conf_file, encoding='utf-8') as conf:
                            for line in conf:
                                if "apiVersion" in line:
                                    serviceApiVersions.append({
                                        'apiVersionFoundIn': conf_file,
                                        'apiVersionLine': line.strip()
                                    })
                    except (FileNotFoundError, UnicodeDecodeError):
                        continue

                    if conf_file.lower().endswith(('.yml', '.yaml')):
                        try:
                            with open(conf_file, "r", encoding="utf-8", errors="ignore") as cf:
                                for line in cf:
                                    if re.search(r'(^|/)v[1-4](/|$)', line):
                                        service_uriversion.append({
                                            'apiVersionFoundIn': conf_file,
                                            'apiVersionLine': line.strip()
                                        })
                        except (FileNotFoundError, UnicodeDecodeError):
                            continue

        if serviceApiVersions:
            apd_Detected['ApiVersioning']['service'].append({
                'serviceName': service['name'],
                'apiVersions': serviceApiVersions
            })

        if service_uriversion:
            apd_Detected['ApiVersioning']["servicehasAPIVersioning"] = True
            apd_Detected['ApiVersioning']['service'].append({
                'serviceName': service['name'],
                'apiVersions': service_uriversion
            })

    for conf_file in metamodel["system"].get("config_files", []):
        try:
            with open(conf_file, encoding='utf-8') as conf:
                for line in conf:
                    if "apiVersion" in line:
                        apd_Detected['ApiVersioning']['system'].append({
                            'apiVersionFoundIn': conf_file,
                            'apiVersionLine': line.strip()
                        })
        except (FileNotFoundError, UnicodeDecodeError):
            continue

    return apd_Detected

############################################################
#                     antipattern 13: HealthCheck
#############################################################
def HealthCheck(metamodel, apd_Detected):
    apd_Detected['HealthCheck'] = {
        'system level': False,
        'service level': False,
        'SystemHealthTools': [],
        'service': []
    }

    try:
        with open("../tools/healthcheck.txt", "r", encoding="utf-8") as sdTools:
            tools = [line.strip() for line in sdTools if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError) as e:
        tools = []
        print(f"Error reading healthcheck tools: {e}")

    for service in metamodel["system"]["microservices"]:
        found_tools = set()
        for dependency in service.get("dependencies", []):
            for tool in tools:
                if tool in dependency:
                    found_tools.add(tool)
        if found_tools:
            apd_Detected['HealthCheck']['service level'] = True
            serviceHT = {
                'serviceName': service['name'],
                'serviceTools': sorted(list(found_tools))
            }
            apd_Detected['HealthCheck']['service'].append(serviceHT)

    system_tools = set()
    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency:
                apd_Detected['HealthCheck']['system level'] = True
                system_tools.add(tool)
    apd_Detected['HealthCheck']['SystemHealthTools'] = sorted(list(system_tools))

    return apd_Detected


############################################################
#                     antipattern 14: LocalLogging
#############################################################

def LocalLogging(metamodel, apd_Detected):
    apd_Detected['LocalLogging'] = {
        'localLoggingState': False,
        'centralizingLoggingState': False,
        'LLInfo': {
            'system level': False,
            'service level': False,
            'systemLoggingTools': [],
            'service': []
        },
        'CLInfo': {
            'system level': False,
            'service level': False,
            'systemLoggingTools': [],
            'service': []
        }
    }

    try:
        with open("../tools/logging.txt", "r", encoding="utf-8") as sdTools:
            tools = [line.strip() for line in sdTools if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError) as e:
        tools = []
        print(f"Error reading logging tools: {e}")

    for service in metamodel["system"]["microservices"]:
        found_tools = set()
        for dependency in service.get("dependencies", []):
            for tool in tools:
                if tool in dependency:
                    found_tools.add(tool)

        if found_tools:
            apd_Detected['LocalLogging']['centralizingLoggingState'] = True
            apd_Detected['LocalLogging']['CLInfo']['service level'] = True
            service_info = {
                'serviceName': service['name'],
                'serviceTools': sorted(list(found_tools))
            }
            apd_Detected['LocalLogging']['CLInfo']['service'].append(service_info)

    system_tools = set()
    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency:
                apd_Detected['LocalLogging']['centralizingLoggingState'] = True
                apd_Detected['LocalLogging']['CLInfo']['system level'] = True
                system_tools.add(tool)

    apd_Detected['LocalLogging']['CLInfo']['systemLoggingTools'] = sorted(list(system_tools))

    try:
        with open("../tools/local_logging.txt", "r", encoding="utf-8") as sdTools:
            tools = [line.strip() for line in sdTools if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError) as e:
        tools = []
        print(f"Error reading logging tools: {e}")

    try:
        with open("../tools/localLogging_imports.txt", "r", encoding="utf-8") as sdTools:
            tools_imports = [line.strip() for line in sdTools if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError) as e:
        tools_imports = []
        print(f"Error reading logging tools: {e}")

    for service in metamodel["system"]["microservices"]:
        found_tools = set()
        found_imports = set()
        for dependency in service.get("dependencies", []):
            for tool in tools:
                if tool in dependency:
                    apd_Detected['LocalLogging']['LLInfo']['service level'] = True
                    found_tools.add(tool)

        imports = service.get("code", {}).get("imports", [])
        for imp in imports:
            for toolimp in tools_imports:
                if toolimp in imp:
                    apd_Detected['LocalLogging']['LLInfo']['service level'] = True
                    found_imports.add(toolimp)

        if found_tools or found_imports:
            apd_Detected['LocalLogging']['localLoggingState'] = True
            apd_Detected['LocalLogging']['LLInfo']['service level'] = True
            service_info = {
                'serviceName': service['name'],
                'serviceTools': sorted(list(found_tools)),
                'serviceImports': sorted(list(found_imports))
            }
            apd_Detected['LocalLogging']['LLInfo']['service'].append(service_info)

    system_tools = set()
    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool in dependency:
                apd_Detected['LocalLogging']['localLoggingState'] = True
                apd_Detected['LocalLogging']['LLInfo']['system level'] = True
                system_tools.add(tool)

    apd_Detected['LocalLogging']['LLInfo']['systemLoggingTools'] = sorted(list(system_tools))

    return apd_Detected


############################################################
#         antipattern 15: InsufficientMonitoring
#############################################################
# Rule : intersect(monitoring libs, dependencies) = 0
def InsufficientMonitoring(metamodel, apd_Detected):
    apd_Detected['InsufficientMonitoring'] = {
        'system level': False,
        'service level': False,
        'systemMonitoringTools': [],
        'service': []
    }

    try:
        with open("../tools/monitoring.txt", "r", encoding="utf-8") as sdTools:
            tools = [line.strip() for line in sdTools if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError) as e:
        tools = []
        print(f"Error reading monitoring tools: {e}")

    # System level
    system_tools = set()
    for dependency in metamodel["system"].get("dependencies", []):
        for tool in tools:
            if tool.lower() in dependency.lower():
                apd_Detected['InsufficientMonitoring']['system level'] = True
                system_tools.add(tool)

    apd_Detected['InsufficientMonitoring']['systemMonitoringTools'] = sorted(system_tools)

    # Microservice level
    # Microservice level
    for service in metamodel["system"].get("microservices", []):
        Sname = service.get('name', '')
        found_tools = set()

        for dependency in service.get("dependencies", []):  # dependency یک رشته است
            dep_lower = dependency.lower()
            for tool in tools:
                if tool.lower() in dep_lower:  # بررسی وجود tool در dependency
                    found_tools.add(tool)

        if found_tools:
            apd_Detected['InsufficientMonitoring']['service level'] = True
            apd_Detected['InsufficientMonitoring']['service'].append({
                'serviceName': service['name'],
                'serviceTools': sorted(found_tools)
            })

    return apd_Detected