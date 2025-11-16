import os
import json
import dependencies
import microservices
import javaparser
import dockerfiles
import shutil
import readProjects as rp
import service_FindURIs
import findAPI
import systemFindURIs

globaladdress = ""
start_time_str = ""
end_time_str = ""
elapsed_time_ms = ""

def main():

    project_root_path, path = rp.readprojects()
    for mbsroot in project_root_path:
        project_name = mbsroot.replace(path, '').lstrip("\\")
        results_dir = os.path.join(r"../result of analysis", project_name)
        globaladdress = results_dir
        gitURL = ""

        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)

        os.makedirs(results_dir)
        metamodel_file = results_dir + "/metamodel.json"

        if os.path.exists(metamodel_file):
            os.remove(
                metamodel_file)

        shutil.copy("../Initial_metamodel.json", metamodel_file)
        with open(metamodel_file, "r") as mm_file:
            mm = json.load(mm_file)

        if gitURL:
            mm["system"]["GitRepository"] = gitURL
        else:
            mm["system"]["GitRepository"] = "NAN"
        ##################################
        # Extracting system dependencies #
        ##################################

        print("Extracting system wide dependencies")
        system_deps = dependencies.extract(mbsroot)
        print("Dependencies extracted, writing to meta-model")

        mm["system"]["dependencies"] = system_deps
        mm_file = open(metamodel_file, "w")
        json.dump(mm, mm_file, indent=4)
        mm_file.close()
        print("Writing done")

        ####################################
        # Extracting root config files     #
        ####################################
        print("Extracting root configuration files")

        system_config = javaparser.getrootconfigfiles(mbsroot)
        systemAllconfig = javaparser.findAllConfigFilesElseWithinMicroservice(mbsroot)

        system_config = system_config + systemAllconfig
        print("Found", len(system_config), "configuration files.\n")

        mm["system"]["config_files"] = system_config
        mm['system']['relations'] = []
        mm['system']['reducedrelations'] = []


        relations, reducedRelations = systemFindURIs.systemFindURIs(mbsroot, results_dir)
        mm['system']['relations'] = relations
        mm['system']['reducedrelations'] = reducedRelations


        try:
            with open(metamodel_file, "w", encoding="utf-8") as mm_file:
                json.dump(mm, mm_file, indent=4)
            print(f"Configuration files saved successfully to '{metamodel_file}'.")
        except Exception as e:
            print(f"An error occurred while writing to '{metamodel_file}': {e}")

        #########################################
        # Extracting All folders in the System  #
        #########################################

        mm["system"]["folders"] = javaparser.list_top_level_folders(mbsroot)

        #########################################
        # Extracting All Dependencies in the System  #
        #########################################
        mm["system"]["dependencies"] = dependencies.extract(mbsroot)
        ########################################
        # Extracting root hardcoded endpoints  #
        ########################################
        print("Starting HTTP config extraction...")

        mm["system"]["http"] = []

        for config_file in mm["system"].get("config_files", []):
            print(f"Extracting HTTP info from: {config_file}")

            # Get HTTP-related data from the config file
            http_data = javaparser.get_http_urls(config_file)

            # Safely add the extracted HTTP data to the list
            if http_data:
                for item in http_data:
                    mm["system"]["http"].append({"url": item['url'],
                                                 "url path": item['path']})
                # Save the updated metamodel to file with safe file handling

        ##################################
        # Extracting microservices       #
        ##################################

        print("Extracting microservices")
        system_ms = microservices.extract(mbsroot)
        mm["system"]["candidateMicroservices"] = {}
        mm["system"]["candidateMicroservices"] = system_ms

        try:
            with open(metamodel_file, "w") as mm_file:
                # Dump JSON with indentation for better readability
                json.dump(mm, mm_file, indent=4)
            print("HTTP configuration extraction and saving completed successfully.")
        except IOError as e:
            # Handle any file writing errors gracefully
            print(f"Failed to write metamodel file: {e}")

        print(system_ms)
        ms_node = []
        customized_list = []
        print("microservices extracted, reading information")

        if not system_ms:
            system_ms = []
            system_ms.append("root")

        for microservice in system_ms:
            ms_data = {}

            #######################################
            customized_Data = {
                "name": "",
                "path": "",
                "dependencies": [],
                "imports": [],
                "annotations": [],
                "declared_annotations": []
            }
            if microservice == "root":
                service_path = mbsroot  # this line is executed when there is only one microservic in the system.
            else:
                service_path = mbsroot + "/" + microservice

            cloc_out = microservices.getlocs(service_path)
            ms_data["name"] = microservice
            customized_Data["name"] = microservice
            customized_Data["path"] = service_path

            ms_data["language"] = dict()
            language, percentage = microservices.getlang(service_path)
            ms_data["language"]["Type"] = language
            ms_data["language"]["Percentage"] = percentage
            ms_data["nb_files"] = cloc_out[0]  # The number of files
            ms_data["locs"] = cloc_out[3]  # The number of lines of code
            ms_data["dependencies"] = dependencies.extract(service_path)
            customized_Data["dependencies"] = ms_data["dependencies"]

            ms_data["code"] = dict()
            ms_data["code"]["file uris"] = []
            ms_data["code"]["file uris"].append(service_FindURIs.findUri(mbsroot, microservice, results_dir))
            ms_data["code"]["class"] = []
            ms_data["code"]["class"] = javaparser.extract_java_classes(service_path)
            ms_data["code"]["imports"] = []
            ms_data["code"]["annotations"] = []
            ms_data["code"].setdefault("declared_annotations", [])
            ms_data["code"]["methods"] = []
            ms_data["code"].setdefault("Fields", [])
            ms_data["code"].setdefault("Local Variables", [])
            ms_data["code"].setdefault("Method Parameters", [])

            ms_data["code"]["http"] = []

            ms_data["code"]["databases"] = dict()
            ms_data["code"]["databases"]["datasources"] = []
            ms_data["code"]["databases"]["create"] = []
            ms_data["code"]["source_files"] = javaparser.getsourcefiles(
                service_path)

            ms_data["config"] = dict()
            ms_data["config"]["config_files"] = javaparser.getconfigfiles(
                service_path)
            ms_data["deployment"] = dict()
            ms_data["deployment"]["docker_files"] = dockerfiles.getdockerfiles(
                service_path)
            ms_data["deployment"]["images"] = []
            ms_data["env"] = dict()
            ms_data["env"]["env_files"] = javaparser.getenvfiles(
                service_path)

            ms_data["code"]["APIs"] = dict()
            ms_data["code"]["APIs"]["number"] = []
            ms_data["code"]["APIs"]["number"] = len(findAPI.find_api_methods(service_path))

            ms_data["code"]["APIs"]["apis"] = []
            ms_data["code"]["APIs"]["apis"] = findAPI.find_api_methods(service_path)

            java_source_file = javaparser.getjavasourcefiles(service_path)
            #####################################################################
            ms_data["code"]["feature_method"] = {}
            features = javaparser.allFeatures_method(service_path)
            ms_data["code"]["feature_method"]["methodReturnType"] = []
            ms_data["code"]["feature_method"]["methodGenericReturnType"] = []
            ms_data["code"]["feature_method"]["methodParamType"] = []
            ms_data["code"]["feature_method"]["methodLocalType"] = []
            for data in features:
                if data["return_type"]:
                    ms_data["code"]["feature_method"]["methodReturnType"].append({
                        "fileName": data["file"],
                        "className": data["class"],
                        "methodName": data["method"],
                        "returnType": data['return_type']
                    })

                if data["generic_return_types"]:
                    ms_data["code"]["feature_method"]["methodGenericReturnType"].append({
                        "fileName": data["file"],
                        "className": data["class"],
                        "methodName": data["method"],
                        "generic_return_types": data['generic_return_types']
                    })

                if data["param_types"]:
                    ms_data["code"]["feature_method"]["methodParamType"].append({
                        "fileName": data["file"],
                        "className": data["class"],
                        "methodName": data["method"],
                        "param_types": data['param_types']
                    })

                if data["local_types"]:
                    ms_data["code"]["feature_method"]["methodLocalType"].append({
                        "fileName": data["file"],
                        "className": data["class"],
                        "methodName": data["method"],
                        "local_types": data['local_types']
                    })

            ###################################################################
            for source in java_source_file:
                print(source)
                tree = javaparser.parse(source)
                ms_data["code"]["annotations"] += javaparser.getannotations(tree, source)
                customized_Data["annotations"] += javaparser.just_getannotations(tree, source)

                ms_data["code"]["declared_annotations"] += javaparser.find_custom_annotations_in_file(source)
                customized_Data["declared_annotations"] += ms_data["code"]["declared_annotations"]

                ms_data["code"]["methods"] += javaparser.getmethods(tree, source)

                ms_data["code"]["imports"] += javaparser.getimports(tree, source)
                customized_Data["imports"] += javaparser.just_getimports(tree, source)

                extracted = javaparser.extract_variable_types(tree)

                ms_data["code"]["Fields"] += extracted.get("Fields", [])

                ms_data["code"]["Local Variables"] += extracted.get("Local Variables", [])
                ms_data["code"]["Method Parameters"] += extracted.get("Method Parameters", [])

                ms_data["code"]["annotations"] = list(dict.fromkeys(ms_data["code"]["annotations"]))
                customized_Data["annotations"] = list(dict.fromkeys(customized_Data["annotations"]))

                ms_data["code"]["methods"] = list(dict.fromkeys(ms_data["code"]["methods"]))

                ms_data["code"]["imports"] = list(dict.fromkeys(ms_data["code"]["imports"]))
                customized_Data["imports"] = list(dict.fromkeys(customized_Data["imports"]))

            httpdb_related = java_source_file + ms_data["config"]["config_files"] + ms_data["env"]["env_files"]
            print(java_source_file)
            print(ms_data["config"]["config_files"])
            print(ms_data["env"]["env_files"])
            for f in httpdb_related:
                print(f)
                http = javaparser.get_http_urls(f)
                for item in http:
                    ms_data["code"]["http"].append({"url": item['url'],
                                                    "url path": item['path']})

                dbsources = javaparser.getdatasourceurls(f)
                dbcreate = javaparser.getcreatedbstatements(f)
                ms_data["code"]["databases"]["datasources"] += dbsources
                ms_data["code"]["databases"]["create"] += dbcreate

                dbsources = javaparser.get_all_datasource_urls(f)
                dbcreate = javaparser.get_createdb_statements_with_type(f)
                ms_data["code"]["databases"]["datasources"] += dbsources
                ms_data["code"]["databases"]["create"] += dbcreate

            # finding images of microservices.
            for dockerfile in ms_data["deployment"]["docker_files"]:
                parsed_dockerfile = dockerfiles.parse(dockerfile)
                ms_data["deployment"]["images"].append(parsed_dockerfile.baseimage)

            ms_node.append(ms_data)
            customized_list.append(customized_Data)

        print("Writing microservices info into meta-model")

        mm_file = open(metamodel_file, "r")
        mm = json.load(mm_file)
        mm_file.close()

        mm["system"]["microservices"] = ms_node

        mm_file = open(metamodel_file, "w")
        json.dump(mm, mm_file, indent=4)
        mm_file.close()
        print("Writing done")

if __name__ == "__main__":
    main()
