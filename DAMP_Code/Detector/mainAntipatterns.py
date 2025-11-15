import json
import FindAntiPatterns as fap
from Extractor import readProjects as rp
import shutil

def writeResults(outputpathResult,nameFile, apd_Detected):

    pathResult= os.path.join(outputpathResult, nameFile)
    with open(pathResult,'w') as f:
        f.write('=========================  General Information of System  =============================\n\n')
        f.write('number of microservices : {ns}\n'.format(ns=apd_Detected['GeneralInformation']['number of services']))
        f.write('Total lines of code (LOCs) : {ns}\n'.format(ns=apd_Detected['GeneralInformation']['total LOCs']))
        f.write('Total number of files : {ns}\n'.format(ns=apd_Detected['GeneralInformation']['total files']))
        f.write('Avg LOCs per service : {ns}\n'.format(ns=apd_Detected['GeneralInformation']['average LOCs']))
        f.write('Avg Files per service : {ns}\n\n'.format(ns=apd_Detected['GeneralInformation']['average files']))
        f.write(f"total number of apis: {apd_Detected['GeneralInformation']['number of apis']}\n\n")
        f.write(f'name of services:\n\n')
        services = apd_Detected['GeneralInformation']["serviceName"]
        for service in services:
            f.write(f'name: {service}\n')
        # =================================================================================================
        f.write(f'#1\n')
        f.write(f'Anti-Pattern Name: {"Wrong Cuts"}\n\n')

        if apd_Detected['WrongCuts']['hasWrongCuts']:
            table_lines = [
                "| Anti-Pattern | Status       |",
                "|--------------|--------------|",
                "| Wrong Cuts   | Detected     |"
            ]

            for line in table_lines:
                f.write(line + "\n")

            for service in apd_Detected['WrongCuts']['services']:
                service_name = service["name"]
                service_type = service["type"]
                count = service["countdataModel"]
                total = service["totalnumber_files"]

                if service_type == "Web":
                    f.write(
                        f'─ [Wrong Cuts - Web] Detected in service: {service_name}. '
                        f'Web-related file count: {count}. Total number of files: {total}.\n'
                    )
                elif service_type == "Datamodel":
                    f.write(
                        f'─ [Wrong Cuts - Datamodel] Detected in service: {service_name}. '
                        f'Data-model annotation count: {count}. Total number of files: {total}.\n'
                    )
                elif service_type == "Logic":
                    f.write(
                        f'─ [Wrong Cuts - Logic] Detected in service: {service_name}. '
                        f'Logic-layer annotation count: {count}. Total number of files: {total}.\n'
                    )
                else:
                    f.write(
                        f'─ [Wrong Cuts - Unknown Type] Detected in service: {service_name}. '
                        f'Count: {count}. Total number of files: {total}.\n'
                    )

        else:
            table_lines = [
                "| Anti-Pattern | Status       |",
                "|--------------|--------------|",
                "| Wrong Cuts   | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")

        f.write('\n===================================================================================\n\n')

        # =================================================================================================

        f.write(f'#2\n')
        f.write(f'Anti-Pattern Name: {"Mega Services"}\n\n')
        if apd_Detected['megaService']['hasMegaService']:
            table_lines = [
                "| Anti-Pattern    | Status       |",
                "|-----------------|--------------|",
                "| Mega Services   | Detected     |"
            ]

            for line in table_lines:
                f.write(line + "\n")

            f.write('\n### Characteristics of Detected Mega Services:\n\n')

            # جدول داده‌ها
            header = "{:<20}  {:>6} {:>15} {:>18} {:>8} {:>10} {:>12}".format(
                "Service Name", "LOCs", "LOC Threshold", "#LOCs in system", "#APIs", "API Ratio", "Total APIs"
            )
            separator = "-" * len(header)
            f.write(header + "\n")
            f.write(separator + "\n")

            for s in apd_Detected['megaService']['characteristics of mega services']:
                row = "{:<20}  {:>6} {:>15.2f} {:>18} {:>8} {:>10.2f} {:>8}".format(
                    s['service name'],
                    s['locs'],
                    s['requiredLocs'],
                    s['total LOCs in system'],
                    s['the number api in MS'],
                    s['api_ratio'],
                    s['total number api in system']
                )
                f.write(row + "\n")

        else:
            table_lines = [
                "| Anti-Pattern    | Status       |",
                "|-----------------|--------------|",
                "| Mega Services   | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")

        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#3\n')
        f.write(f'Anti-Pattern Name: {"Nano Services"}\n\n')
        if apd_Detected['nanoService']['hasNanoService']:
            table_lines = [
                "| Anti-Pattern    | Status       |",
                "|-----------------|--------------|",
                "| Nano Services   | Detected     |"
            ]

            for line in table_lines:
                f.write(line + "\n")

            f.write('\n### Characteristics of Detected Nano Services:\n\n')

            header = "{:<20}  {:>6} {:>15} {:>18} {:>8} {:>10} {:>12}".format(
                "Service Name", "LOCs", "LOC Threshold", "#LOCs in system", "#APIs", "API Ratio", "Total APIs"
            )
            separator = "-" * len(header)
            f.write(header + "\n")
            f.write(separator + "\n")

            for s in apd_Detected["nanoService"]["characteristics of nano services"]:
                row = "{:<20}  {:>6} {:>15.2f} {:>18} {:>8} {:>10.2f} {:>8}".format(
                    s['service name'],
                    s['locs'],
                    s['requiredLocs'],
                    s['total LOCs in system'],
                    s['number api in service'],
                    s['api_ratio'],
                    s['total number api in system']
                )
                f.write(row + "\n")

        else:
            table_lines = [
                "| Anti-Pattern    | Status       |",
                "|-----------------|--------------|",
                "| Nano Services   | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")

        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#4\n')
        f.write(f'Anti-Pattern Name: {"Shared Libraries"}\n\n')

        if apd_Detected['sharedDependencies']["hasSharedDependency"]:
            table_lines = [
                "| Anti-Pattern     | Status       |",
                "|------------------|--------------|",
                "| Shared Libraries | Detected     |"
            ]

            for line in table_lines:
                f.write(line + "\n")

            f.write('\n### Characteristics of Detected Shared Libraries:\n\n')

            # Shared Libraries in config dependencies
            if apd_Detected['sharedDependencies']["dependency in config file"]:
                f.write('\n*** Shared Libraries in dependencies (Maven or Gradle files) were found:\n\n')
                f.write("{:<40} {:<60}\n".format("Dependency", "Used By Services"))
                f.write("-" * 100 + "\n")

                for item in apd_Detected["sharedDependencies"]["dependency in config file"]:
                    dep = item["dependency"]
                    services = ", ".join(item["services"])
                    f.write("{:<40} {:<60}\n".format(dep, services))

                f.write("-" * 100 + "\n\n")

            # Dependencies via code-level imports
            if apd_Detected['sharedDependencies']["dependency in imported section"]:
                f.write(f"\n*** Dependencies among microservices are established through code-level imports,"
                        f" where services directly reference each other's components:\n\n")

                f.write("{:<40} {:<60}\n".format("Microservice", "Uses"))
                f.write("-" * 100 + "\n")

                for k, v in apd_Detected['sharedDependencies']["dependency in imported section"].items():
                    # uses = ", ".join(v)
                    for uses in v:
                        f.write("{:<40} {:<60}\n".format(k, uses))

                f.write("-" * 100 + "\n\n")


            if apd_Detected['sharedDependencies']["sharedLibrariesWithFilePath"]:
                for serv, path in apd_Detected['sharedDependencies']["sharedLibrariesWithFilePath"].items():
                    f.write(f'\n the service  is {serv} and the location servive imported is :\n-')
                    for p in path:
                        f.write(f'- {p["service imported"]},{p["file path"]}\n')
                    f.write(f'\n *********************\n')
        else:
            table_lines = [
                "| Anti-Pattern     | Status       |",
                "|------------------|--------------|",
                "| Shared Libraries | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")

        f.write('\n===================================================================================\n\n')
        # =================================================================================================

        f.write('#5\n')
        f.write("Anti-Pattern Name: Hardcoded Endpoints\n\n")

        hardcoded = apd_Detected.get("hardcodedEndpoints", {})
        has_hardcoded = hardcoded.get("hashardcodedEndpoints", False)
        has_sd_tools = hardcoded.get("hasServiceDiscoveryTools", False)

        if has_hardcoded:
            f.write("| Anti-Pattern        | Status   |\n")
            f.write("|---------------------|----------|\n")
            f.write("| Hardcoded Endpoints | ======== |\n\n")

            services = hardcoded.get("service", [])
            if services:
                for service in services:
                    urls = service.get("FoundUrls", [])
                    url_paths = service.get("UrlPath", [])
                    if urls:
                        f.write(f'- Service `{service.get("service name", "UNKNOWN")}` has hardcoded HTTP URLs:\n')
                        for i, url in enumerate(urls):
                            path = url_paths[i] if i < len(url_paths) else ""
                            f.write(f'  - {url}, path: {path}\n')
                        f.write("\n")

            system_urls = hardcoded.get("system", {}).get("FoundUrls", [])
            system_paths = hardcoded.get("system", {}).get("UrlPath", [])
            if system_urls:
                f.write('- System has hardcoded HTTP URLs:\n\n')
                for i, url in enumerate(system_urls):
                    path = system_paths[i] if i < len(system_paths) else ""
                    f.write(f'  - {url}, path: {path}\n')
                f.write("\n")

            if has_sd_tools:
                system_tools = hardcoded.get("system", {}).get("ServiceDiscoveryTool", [])
                unique_system_tools = list(set(system_tools))
                if unique_system_tools:
                    f.write(" **System-level Tools**:\n")
                    for tool in unique_system_tools:
                        f.write(f"- {tool}\n")
                    f.write("\n--------------------------------------------------------\n\n")

                services_with_tools = [s for s in services if s.get("ServiceDiscoveryTool")]
                if services_with_tools:
                    f.write(" **Service-level Tools**:\n\n")
                    for service in services_with_tools:
                        tools = service.get("ServiceDiscoveryTool", [])
                        f.write(f"- `{service.get('service name', 'UNKNOWN')}`:\n")
                        for tool in tools:
                            f.write(f"  - {tool}\n")
                        f.write("\n")

        elif has_sd_tools:
            f.write("| Anti-Pattern        | Status       |\n")
            f.write("|---------------------|--------------|\n")
            f.write("| Hardcoded Endpoints | Not detected |\n\n")

            system_tools = hardcoded.get("system", {}).get("ServiceDiscoveryTool", [])
            unique_system_tools = list(set(system_tools))
            if unique_system_tools:
                f.write(" **System-level Tools**:\n")
                for tool in unique_system_tools:
                    f.write(f"- {tool}\n")
                f.write("\n--------------------------------------------------------\n\n")

            services = hardcoded.get("service", [])
            services_with_tools = [s for s in services if s.get("ServiceDiscoveryTool")]
            if services_with_tools:
                f.write(" **Service-level Tools**:\n\n")
                for service in services_with_tools:
                    tools = service.get("ServiceDiscoveryTool", [])
                    f.write(f"- `{service.get('service name', 'UNKNOWN')}`:\n")
                    for tool in tools:
                        f.write(f"  - {tool}\n")
                    f.write("\n")

        else:
            f.write("| Anti-Pattern        | Status       |\n")
            f.write("|---------------------|--------------|\n")
            f.write("| Hardcoded Endpoints | Not detected |\n\n")

        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#6\n')
        f.write("Anti-Pattern Name: Manual Configuration\n\n")
        if apd_Detected["manualConfiguration"]["system"]["hasConfigurationTool"] or \
                sum(len(service.get("FoundConfigFiles", [])) for service in
                    apd_Detected["manualConfiguration"]["service"]):

            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| Manual Configuration | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")
            f.write(
                f'\n\n Auto-configuration tools have been detected in the system; therefore, the Manual Configuration anti-pattern does not exist.\n\n')
            f.write("\n\n### Characteristics of Auto Configuration:\n\n")

            system_tools = apd_Detected["manualConfiguration"]["system"].get("hasConfigurationTool", [])
            if system_tools:
                unique_tools = list(set(system_tools))
                if unique_tools:
                    f.write(" **System-level Tools**:\n")
                    for tool in unique_tools:
                        f.write(f"- {tool}\n")
                    f.write("\n------------------------------\n\n")

            services_with_tools = [
                s for s in apd_Detected["manualConfiguration"]["service"]
                if s.get("FoundConfigFiles")
            ]
            if services_with_tools:
                f.write(" **Service-level Tools**:\n\n")
                for service in services_with_tools:
                    tools = service["FoundConfigFiles"]
                    f.write(f"- `{service['service name']}`:\n")
                    for tool in tools:
                        f.write(f"  - {tool}\n")
                    f.write("\n")
        else:
            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| Manual Configuration | Detected     |"
            ]

            for line in table_lines:
                f.write(line + "\n")

        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#7\n')
        f.write('Anti-Pattern Name: {name}\n\n'.format(name='NoCICD (Missing CI/CD Pipeline)'))
        if apd_Detected["NoCICD"]['system']['system level']:
            table_lines = [
                "| Anti-Pattern | Status       |",
                "|--------------|--------------|",
                "| NoCICD       | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")
            f.write(f'\n## CI/CD Pipeline has been found.\n')
            f.write('\n---------- Detection Details in the System Level ---------- \n')
            if apd_Detected["NoCICD"]['system']['hasCiCdFolders']:
                f.write('- Detected CI/CD Folders: {value}\n'.
                    format(value=apd_Detected["NoCICD"]['system']['hasCiCdFolders']))

            if apd_Detected["NoCICD"]['system']['hasConfigCiCD']:
                f.write('- Detected CI/CD Configuration Files: {value}\n'.
                        format(value=apd_Detected["NoCICD"]['system']['hasConfigCiCD']))

            if apd_Detected["NoCICD"]['system']['hasDependencyCiCD']:
                f.write(f'- Detected CI/CD Dependencies: {apd_Detected["NoCICD"]["system"]["hasDependencyCiCD"]}\n')

            if apd_Detected["NoCICD"]['system']['hasKeywordsCiCD']:
                f.write('- Detected CI/CD Keywords in config files: {value}\n'.
                    format(value=apd_Detected["NoCICD"]['system']['hasKeywordsCiCD']))

        elif apd_Detected["NoCICD"]['service']['service name']:
            table_lines = [
                "| Anti-Pattern | Status       |",
                "|--------------|--------------|",
                "| NoCICD       | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")
            f.write(f'\n## CI/CD Pipeline was found.\n')
            f.write('\n---------- Detection Details in the Service Level ---------- \n')
            for s in range(len(apd_Detected["NoCICD"]['service']['service name'])):
                f.write('-----------------------------------------------------------------------')
                f.write('- Service Name: {value}\n'.
                        format(value=apd_Detected["NoCICD"]['service']['service name']))

                if apd_Detected["NoCICD"]['service']['hasCiCdFolders']:
                    f.write(f'- Detected CI/CD Folders: {apd_Detected["NoCICD"]["service"]["hasCiCdFolders"]}\n')

                if apd_Detected["NoCICD"]['service']['hasConfigCiCD']:
                    f.write('- Detected CI/CD Configuration Files: {value}\n'.
                        format(value=apd_Detected["NoCICD"]['service']['hasConfigCiCD']))

                if apd_Detected["NoCICD"]['service']['hasDependencyCiCD']:
                    f.write('- Detected CI/CD Dependencies: {value}\n'.
                        format(value=apd_Detected["NoCICD"]['service']['hasDependencyCiCD']))

                if apd_Detected["NoCICD"]['service']['hasKeywordsCiCD']:
                    f.write('- Detected CI/CD Keywords in config files: {value}\n'.
                        format(value=apd_Detected["NoCICD"]['service']['hasKeywordsCiCD']))

        else:
                table_lines = [
                    "| Anti-Pattern | Status   |",
                    "|--------------|----------|",
                    "| NoCICD       | Detected |"
                ]

                for line in table_lines:
                    f.write(line + "\n")
                f.write(f'\n\n - The system lacks any CI/CD pipeline tools.\n')

        f.write('\n===================================================================================\n\n')

        # =================================================================================================
        f.write(f'#8\n')
        f.write("Anti-Pattern Name: No API Gateway (NAG)\n\n")
        if apd_Detected["apiGateway"]["system"]["system level"] or \
                sum(len(service.get("service dependencies", [])) for service in
                    apd_Detected["apiGateway"]["service"]):

            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| No API Gateway (NAG) | Not detected |"
            ]

            for line in table_lines:
                f.write(line + "\n")
            f.write(f"\n\n The code contains API Gateway tools.\n\n")
            f.write("\n\n### Characteristics of API Gateway:\n\n")

            system_tools = apd_Detected["apiGateway"]["system"].get("system dependency", [])
            if system_tools:
                unique_tools = list(set(system_tools))
                if unique_tools:
                    f.write(" **System-level Tools**:\n")
                    for tool in unique_tools:
                        f.write(f"- {tool}\n")
                    f.write("\n------------------------------\n\n")

            services_with_tools = [
                s for s in apd_Detected["apiGateway"]["service"]
                if s.get("service dependencies")
            ]
            if services_with_tools:
                f.write(" **Service-level Tools**:\n\n")
                for service in services_with_tools:
                    tools = service["service dependencies"]
                    f.write(f"- `{service['service name']}`:\n")
                    for tool in tools:
                        f.write(f"  - {tool}\n")
                    f.write("\n")
        else:
            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| No API Gateway (NAG) | Detected     |"
            ]

            for line in table_lines:
                f.write(line + "\n")
            f.write(f'\n\nNo API Gateway tools were detected in the system\n\n')

        f.write('\n===================================================================================\n\n')
        # =================================================================================================

        f.write(f'#9\n')
        f.write("Anti-Pattern Name: Timeouts (TO)\n\n")

        if apd_Detected['Timeouts']["flagTO"]:

            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| Timeouts (TO)        | Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")


            f.write(f'\n- The Timeout pattern was identified at the service level.\n\n')

            for s in apd_Detected["Timeouts"]["service"]:
                f.write(f"Service: {s['service name']}\n")

                if s['service dependency']:
                    f.write(f"  - Dependencies:\n")
                    for dep in s['service dependency']:
                        f.write(f"    - {dep}\n")

                if s["hasTOImports"]:
                    f.write(f"  - Timeout Imports:\n")
                    for imp in s["ToImports"]:
                        f.write(f"    - {imp}\n")

                if s["hasFBImports"]:
                    f.write(f"  - Fallback Imports:\n")
                    for imp in s["FbImports"]:
                        f.write(f"    - {imp}\n")

                if s["hasTOMethods"]:
                    f.write(f"  - Timeout Methods:\n")
                    for m in s["ToMethods"]:
                        try:
                            path, method = m.rsplit('/', 1)
                            file_name = os.path.basename(path)
                            f.write(f"    - {file_name} / {method}\n")
                        except:
                            f.write(f"    - {m}\n")

                if s["hasFBMethods"]:
                    f.write(f"  - Fallback Methods:\n")
                    for m in s["FbMethods"]:
                        try:
                            path, method = m.rsplit('/', 1)
                            file_name = os.path.basename(path)
                            f.write(f"    - {file_name} / {method}\n")
                        except:
                            f.write(f"    - {m}\n")

                f.write("\n---\n")

        elif not apd_Detected['Timeouts']["flagTO"]:
            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| Timeouts (TO)        | Not detected |"
            ]
            for line in table_lines:
                f.write(line + "\n")
        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#10\n')
        f.write("Anti-Pattern Name: Multiple Services Per Host (MSPH)\n\n")
        hasDockerFileFlag = any(
            service.get('hasDockerFile')
            for service in apd_Detected['MultipleServicesPerHost']['service']
        )

        if apd_Detected['MultipleServicesPerHost']["system"]["hasDockerCompose"] or hasDockerFileFlag :

            table_lines = [
                "| Anti-Pattern                     | Status       |",
                "|----------------------------------|--------------|",
                "| Multiple Services Per Host (MSPH)| Not detected |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write(f'\n\n')
            if apd_Detected['MultipleServicesPerHost']["system"]["hasDockerCompose"]:
                f.write(f'- The system includes a docker-compose file.\n')

            if hasDockerFileFlag:
                for service in apd_Detected['MultipleServicesPerHost']['service']:
                    if service['hasDockerFile']:
                        f.write(f'- service {service["service name"]} has a Dockerfile\n')
        else:
            table_lines = [
                "| Anti-Pattern                     | Status       |",
                "|----------------------------------|--------------|",
                "| Multiple Services Per Host (MSPH)| Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")

            f.write(f'- No docker-compose file or Dockerfile was found in the system.\n\n')
        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#11\n')
        f.write("Anti-Pattern Name: Shared Persistence\n\n")
        if any(len(list(dict.fromkeys(service['services']))) > 1 for service in
               apd_Detected["SharedPersistence"]["sharedDatabases"]):

            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| Shared Persistence   | Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')

            for service in apd_Detected["SharedPersistence"]["sharedDatabases"]:
                print(service)
                unique_services = list(dict.fromkeys(service['services']))

                if len(unique_services) > 1:
                    f.write( f"- Database {service['database']} with type {service['type']} is shared between {unique_services}.\n\n")

        else:
                table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| Shared Persistence   | Not detected |"
                ]
                for line in table_lines:
                    f.write(line + "\n")
                f.write('\n\n')
                f.write(f'- No shared databases were found among the microservices.')
        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#12\n')
        f.write("Anti-Pattern Name: No API Versioning\n\n")
        serviceApiVersioning = apd_Detected['ApiVersioning']["servicehasAPIVersioning"]

        if apd_Detected['ApiVersioning']["SystemhasAPIVersioning"] or serviceApiVersioning:
            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| No API Versioning    | Not detected |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')

            if apd_Detected['ApiVersioning']["SystemhasAPIVersioning"]:
                f.write(f'- The API versioning tool in the system level was detected.\n\n')
                seen = set()
                for sys in apd_Detected['ApiVersioning']['system']:
                    key = (sys["apiVersionFoundIn"], sys["apiVersionLine"])
                    if key not in seen:
                        seen.add(key)
                        f.write(f' API Version found in {sys["apiVersionFoundIn"]} as {sys["apiVersionLine"]}\n')

            if apd_Detected['ApiVersioning']["systemUri"]:
                f.write(f'- The uri versioning in the system level was detected.\n\n')
                for ur in set(apd_Detected['ApiVersioning']["systemUri"]):
                    f.write(f' uri Version found in {ur}\n')

            if serviceApiVersioning:
                seen = set()
                for service in apd_Detected['ApiVersioning']['service']:
                    for version in service["apiVersions"]:
                        key = (service["serviceName"], version["apiVersionFoundIn"], version["apiVersionLine"])
                        if key not in seen:
                            seen.add(key)
                            f.write(f'- In service {service["serviceName"]}, '
                                    f'API versioning was observed in the configuration file {version["apiVersionFoundIn"]}'
                                    f' as follows "{version["apiVersionLine"]}".\n')

        else:
            table_lines = [
                "| Anti-Pattern         | Status       |",
                "|----------------------|--------------|",
                "| No API Versioning    | Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')
            f.write(f'No API versioning tool was found.\n\n')
        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#13\n')
        f.write("Anti-Pattern Name: No Health Check\n\n")
        if apd_Detected['HealthCheck']['system level'] or apd_Detected['HealthCheck']['service level']:
            table_lines = [
                "| Anti-Pattern     | Status       |",
                "|------------------|--------------|",
                "| No Health Check  | Not detected |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')

            if apd_Detected['HealthCheck']['system level']:
                f.write(f'- Health Check tool in the system level was detected.\n\n')
                for sys in apd_Detected['HealthCheck']['SystemHealthTools']:
                    f.write(f' Health Check tool found in {sys}.\n')

            if apd_Detected['HealthCheck']['service level']:
                for service in apd_Detected['HealthCheck']['service']:
                    f.write(f'- In service {service["serviceName"]}, '
                            f'Health Check was observed in the  {service["serviceTools"]}.\n\n')


        else:
            table_lines = [
                "| Anti-Pattern     | Status       |",
                "|------------------|--------------|",
                "| No Health Check  | Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')
            f.write(f'No Health Check tool was found.\n\n')
        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        f.write(f'#14\n')
        f.write("Anti-Pattern Name: Local Logging (LL)\n\n")
        if apd_Detected['LocalLogging']['centralizingLoggingState'] :
            table_lines = [
                "| Anti-Pattern        | Status       |",
                "|---------------------|--------------|",
                "| Local Logging (LL)  | Not detected |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')

            if apd_Detected['LocalLogging']['CLInfo']['system level']:
                f.write(f'- Centralized Logging tool in the system level was detected.\n')
                for sys in apd_Detected['LocalLogging']['CLInfo']['systemLoggingTools']:
                    f.write(f'    ** Centralized Logging tool found in {sys}.\n')

            if apd_Detected['LocalLogging']['CLInfo']['service level']:
                f.write(f'\n- Centralized Logging tool in the service level was detected.\n')
                for service in apd_Detected['LocalLogging']['CLInfo']['service']:
                    f.write(f'    ** In service {service["serviceName"]}, '
                            f'Centralized Logging was observed in the {service["serviceTools"]}.\n')
            f.write("\n\n *****************Aditional Information****************")
            if apd_Detected['LocalLogging']['LLInfo']['system level']:
                f.write(f'- Local Logging antipattern in the system level was detected.\n')
                for sys in apd_Detected['LocalLogging']['LLInfo']['systemLoggingTools']:
                    f.write(f'    ** Local Logging tool found in {sys}.\n')

            if apd_Detected['LocalLogging']['LLInfo']['service level']:
                f.write(f'\n- Local Logging tool in the service level was detected.\n')
                for service in apd_Detected['LocalLogging']['LLInfo']['service']:
                    f.write(f'    ** In service {service["serviceName"]}:\n ')
                    if service["serviceTools"]:
                        f.write(f'        -Local Logging was observed in the {service["serviceTools"]} dependencies.\n')
                    if service["serviceImports"]:
                        f.write(f'        -Local Logging was observed in the {service["serviceImports"]} imports.\n')
                    f.write(f'\n\n')
        else:
            table_lines = [
                "| Anti-Pattern       | Status       |",
                "|--------------------|--------------|",
                "| Local Logging (LL) | Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')
            f.write(f'The characteristics of local logging are as follows.\n\n')
            if apd_Detected['LocalLogging']['LLInfo']['system level']:
                f.write(f'- Local Logging antipattern in the system level was detected.\n')
                for sys in apd_Detected['LocalLogging']['LLInfo']['systemLoggingTools']:
                    f.write(f'    ** Local Logging tool found in {sys}.\n')

            if apd_Detected['LocalLogging']['LLInfo']['service level']:
                f.write(f'\n- Local Logging tool in the service level was detected.\n')
                for service in apd_Detected['LocalLogging']['LLInfo']['service']:
                    f.write(f'    ** In service {service["serviceName"]}:\n ')
                    if service["serviceTools"]:
                        f.write(f'        -Local Logging was observed in the {service["serviceTools"]} dependencies.\n')
                    if service["serviceImports"]:
                        f.write(f'        -Local Logging was observed in the {service["serviceImports"]} imports.\n')
                    f.write(f'\n\n')

        f.write('\n===================================================================================\n\n')
        # =================================================================================================
        # =================================================================================================
        f.write(f'#15\n')
        f.write("Anti-Pattern Name: Insufficient Monitoring\n\n")
        if apd_Detected['InsufficientMonitoring']['system level'] or apd_Detected['InsufficientMonitoring'][
            'service level']:
            table_lines = [
                "| Anti-Pattern            | Status       |",
                "|-------------------------|--------------|",
                "| Insufficient Monitoring | Not detected |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')

            if apd_Detected['InsufficientMonitoring']['system level']:
                f.write(f'- Monitoring tool in the system level was detected.\n')
                for sys in apd_Detected['InsufficientMonitoring']['systemMonitoringTools']:
                    f.write(f'    ** Monitoring tool found in {sys}.\n')

            if apd_Detected['InsufficientMonitoring']['service level']:
                f.write(f'\n- Monitoring tool in the service level was detected.\n')
                for service in apd_Detected['InsufficientMonitoring']['service']:
                    f.write(f'    ** In service {service["serviceName"]}, '
                            f'Monitoring was observed in the {service["serviceTools"]}.\n')
        else:
            table_lines = [
                "| Anti-Pattern            | Status       |",
                "|-------------------------|--------------|",
                "| Insufficient Monitoring | Detected     |"
            ]
            for line in table_lines:
                f.write(line + "\n")
            f.write('\n\n')
            f.write(f'No Monitoring tool was found.\n\n')
        f.write('\n===================================================================================\n\n')
        # =================================================================================================

import os


if __name__ == "__main__":
    features = []
    # maf.main()
    project_root_path, path = rp.readprojects()
    for mbsroot in project_root_path:
        project_name = mbsroot.replace(path, '').lstrip("\\")
        print(f' project name is: {project_name}')
        proj = os.path.join(r"../result of analysis", project_name)
        results_dir = os.path.join(proj, 'OutputDetection')
        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)

        os.makedirs(results_dir)

        apd_Detected = dict()
        metamodel_file = os.path.join(proj, 'metamodel.json')
        with open(metamodel_file) as mmfile:
            metamodel = json.load(mmfile)
        fap.generalInformation(metamodel, apd_Detected)
        fap.WrongCuts(metamodel, apd_Detected)
        fap.megaService(metamodel, apd_Detected)
        fap.nanoService(metamodel, apd_Detected)
        fap.sharedDependencies(metamodel, apd_Detected)
        fap.hardcodedEndpoints(metamodel, apd_Detected)
        fap.manualConfiguration(metamodel, apd_Detected)
        fap.NoCiCd(metamodel, apd_Detected)
        fap.apiGateway(metamodel, apd_Detected)
        fap.Timeouts(metamodel, apd_Detected)
        fap.MultipleServicesPerHost(metamodel, apd_Detected)
        fap.SharedPersistence(metamodel, apd_Detected)
        fap.ApiVersioning(metamodel, apd_Detected)
        fap.HealthCheck(metamodel, apd_Detected)
        fap.LocalLogging(metamodel, apd_Detected)
        fap.InsufficientMonitoring(metamodel, apd_Detected)

        writeResults(results_dir, 'APD_results.txt', apd_Detected)