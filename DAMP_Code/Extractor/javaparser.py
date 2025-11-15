import glob
import javalang
import json
import os
import re

def getsourcefiles(service_path):
    listeFichiers = []
    for (repertoire, sousRepertoires, fichiers) in os.walk(service_path):
        for fichier in fichiers:

            full_path = os.path.join(repertoire, fichier)
            listeFichiers.append(full_path)
    return listeFichiers
#######################################################################################
def getjavasourcefiles(service_path):

    source_files = []
    with open("files_needles/source_files.txt", "r") as files:
        possibles = files.read().splitlines()

        for possible in possibles:
            fileslist = glob.glob(service_path + "/**/" + possible, recursive=True)

            for f in fileslist:
                if "test" not in f.lower():
                    source_files.append(f)
    return source_files
#######################################################################################
def getconfigfiles(service_path):
    config_files = []
    with open("files_needles/config_files.txt", "r") as files:
        possibles = files.read().splitlines()
        for possible in possibles:
            fileslist = glob.glob(service_path + "/**/" + possible, recursive=True)
            for f in fileslist:
                if "test" not in f.lower():
                    config_files.append(f)
        print(config_files)
        return config_files
#######################################################################################
def getrootconfigfiles(service_path):
    config_files = []
    with open("files_needles/config_files.txt", "r") as files:

        possibles = files.read().splitlines()
        for possible in possibles:
            fileslist = glob.glob(service_path + "/" + possible, recursive=True)
            for f in fileslist:

                if "test" not in f.lower() :
                    config_files.append(f)
        return config_files


#######################################################################################
CONFIG_EXTENSIONS = [
    ".properties", ".cnf", ".conf", ".sql", ".yml", ".yaml", ".xml"
]

SPECIAL_FILES = {
    "Jenkinsfile",
    ".gitlab-ci.yml",
    ".travis.yml",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
    ".drone.yml",
    "buildkite.yml",
}

SPECIAL_PATHS = [
    ".github/workflows/*.yml",
    ".circleci/config.yml",
    ".buildkite/pipeline.yml"
]

#######################################################################################
def contains_java_files(folder):
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            if f.endswith(".java"):
                return True
    return False
#######################################################################################
def find_config_in_folder(folder):
    config_files = []

    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            if (
                    Path(f).suffix in CONFIG_EXTENSIONS
                    or f in SPECIAL_FILES
            ):
                config_files.append(str(Path(dirpath) / f))

    for special_pattern in SPECIAL_PATHS:
        for p in Path(folder).glob(special_pattern):
            if p.is_file():
                config_files.append(str(p.resolve()))

    return config_files

#######################################################################################
from pathlib import Path
def findAllConfigFilesElseWithinMicroservice(root_path):
    all_config_files = []
    root_path = Path(root_path)

    for item in root_path.iterdir():
        if item.is_dir():
            if contains_java_files(item):
                continue
            configs = find_config_in_folder(item)
            if configs:
                all_config_files.extend(configs)

    result = {"configfiles": all_config_files}

    with open(os.path.join(root_path, "config_files.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    return all_config_files
#######################################################################################
def getenvfiles(service_path):

    env_files = []

    with open("files_needles/env_files.txt", "r") as files:

        possibles = files.read().splitlines()
        for possible in possibles:

            fileslist = glob.glob(service_path + "/**/" + possible, recursive=True)
            for f in fileslist:

                if "test" not in f.lower():

                    env_files.append(f)

        return env_files
#######################################################################################
def parse(source_file):
    with open(source_file, "r") as file:
        content = file.read()
    return javalang.parse.parse(content)
#######################################################################################
def getmethods(tree, source):
    method = []
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        method.append(source+"/"+node.name)
    return method
#######################################################################################
def getannotations(tree, source):
    annotations = []
    for path, node in tree.filter(javalang.tree.Annotation):
        annotations.append( source+"/"+node.name)
    return annotations
#######################################################################################
def just_getannotations(tree, source):
    annotations = []
    for path, node in tree.filter(javalang.tree.Annotation):
        annotations.append(node.name)
    return annotations
#######################################################################################
def get_full_type(type_node):
    if type_node is None:
        return None
    base_type = type_node.name if hasattr(type_node, 'name') else str(type_node)
    if hasattr(type_node, 'arguments') and type_node.arguments:
        generics = []
        for arg in type_node.arguments:
            if hasattr(arg, 'type'):
                generics.append(get_full_type(arg.type))
            else:
                generics.append(str(arg))
        return f"{base_type}<{', '.join(g if g is not None else '' for g in generics)}>"

    else:
        return base_type
#######################################################################################
def extract_variable_types(tree):
    results = {
        "Fields": [],
        "Local Variables": [],
        "Method Parameters": []
    }
    for path, node in tree.filter(javalang.tree.FieldDeclaration):
        var_type = get_full_type(node.type)
        for declarator in node.declarators:
            results["Fields"].append({
                "name": declarator.name,
                "type": var_type
            })

    for path, node in tree.filter(javalang.tree.LocalVariableDeclaration):
        var_type = get_full_type(node.type)
        for declarator in node.declarators:
            results["Local Variables"].append({
                "name": declarator.name,
                "type": var_type
            })

    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        if node.parameters:
            for param in node.parameters:
                param_type = get_full_type(param.type)
                results["Method Parameters"].append({
                    "name": param.name,
                    "type": param_type
                })

    return results
#######################################################################################
def find_custom_annotations_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    matches = re.findall(r'@interface\s+(\w+)', content)
    return matches
#######################################################################################
def find_custom_annotations_in_project(root_dir):
    custom_annotations = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.java'):
                full_path = os.path.join(dirpath, filename)
                custom_annotations += find_custom_annotations_in_file(full_path)
    return custom_annotations
#######################################################################################
def getimports(tree, source):
    imports = []
    for path, node in tree.filter(javalang.tree.Import):
        imports.append( source+"/"+node.path)
    return imports

#######################################################################################
def just_getimports(tree, source):
    imports = []
    for path, node in tree.filter(javalang.tree.Import):
        imports.append(node.path)
    return imports

#######################################################################################
def get_http_urls(source_path):
  url_infos = []

  try:
      with open('tools/tlds.txt', 'r') as tlds_file:

          excluded_tlds = [line.strip() for line in tlds_file if line.strip()]
  except FileNotFoundError:
      print("TLDs file not found. Proceeding without exclusion list.")
      excluded_tlds = []


  try:
      with open(source_path, 'r', encoding='utf-8') as source_file:

          content = source_file.read()

          content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

  except Exception as e:
      print(f"Error reading source file {source_path}: {e}")
      return []

  http_regex = r"((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&]*(#!)?)*)"

  matches = re.findall(http_regex, content)

  if matches:

      for match in matches:

          url = match[0]

          if not any(tld in url for tld in excluded_tlds) and len(url) > 8:

              url_infos.append({
                  "url": url,
                  "path": source_path
              })

  return url_infos
#######################################################################################
def remove_line_comments_safe(code):
    result = []
    in_string = False
    escape = False

    for line in code.splitlines():
        new_line = ""
        i = 0
        while i < len(line):
            char = line[i]

            if char == '"' and not escape:
                in_string = not in_string
                new_line += char
            elif char == "\\" and not escape:
                escape = True
                new_line += char
                i += 1
                if i < len(line):
                    new_line += line[i]
                escape = False
            elif not in_string and char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                break  # Ignore the rest of the line (comment found)
            else:
                new_line += char
            i += 1
        result.append(new_line)
    return "\n".join(result)

#######################################################################################
def getdatasourceurls(source):

    ds_urls = []


    with open(source, "r") as f:
        content = f.read().splitlines()

        for line in content:
            if "mysql://" in line:

                line = line.replace('"', " ").replace("'", " ").replace(",", " ")

                ds_urls.append(line.split("mysql://")[1].split()[0])
    return list(set(ds_urls))
#######################################################################################
def get_all_datasource_urls(source):

    keywords = {
        "mysql://": r"mysql://([^\s\"',;]+)",
        "postgresql://": r"postgresql://([^\s\"',;]+)",
        "sqlserver://": r"sqlserver://([^\s\"',;]+)",
        "mongodb://": r"mongodb://([^\s\"',;]+)",
        "oracle:": r"oracle:([^\s\"',;]+)",
        "jdbc:postgresql://": r"jdbc:postgresql://([^\s\"',;]+)",
        "jdbc:mysql://": r"jdbc:mysql://([^\s\"',;]+)",
        "jdbc:sqlserver://": r"jdbc:sqlserver://([^\s\"',;]+)",
        "jdbc:oracle:thin:@": r"jdbc:oracle:thin:@([^\s\"',;]+)"
    }
    import re
    ds_urls = []

    with open(source, "r") as f:
        content = f.read()

        for key, pattern in keywords.items():
            matches = re.findall(pattern, content)
            ds_urls.extend(matches)

    return list(set(ds_urls))
#######################################################################################
def getcreatedbstatements(source):
    cdb_statements = []
    with open(source, "r") as f:
        content = f.read().splitlines()

        for line in content:
            line_lower = line.lower().replace(";", " ")


            if "create database if not exists" in line_lower:
                print(line_lower)


                parts = line_lower.split("exists")
                if len(parts) > 1:
                    tokens = parts[1].split()
                    if tokens:
                        cdb_statements.append(tokens[0])
                continue

            elif "create database" in line_lower:
                print(line_lower)
                parts = line_lower.split("create database")
                if len(parts) > 1:
                    tokens = parts[1].split()
                    if tokens:
                        cdb_statements.append(tokens[0])


    return list(set(cdb_statements))
#######################################################################################
def get_createdb_statements_with_type(source):
    cdb_statements = []

    with open(source, "r") as f:
        content = f.read().splitlines()

        for line in content:
            lower_line = line.lower().strip()

            # MySQL, PostgreSQL, SQL Server, Oracle
            if "create database if not exists" in lower_line:
                name = lower_line.replace(";", " ").split("exists")[1].split()[0]
                cdb_statements.append({"name": name, "type": "sql"})

            elif "create database" in lower_line:
                name = lower_line.replace(";", " ").split("create database")[1].split()[0]
                cdb_statements.append({"name": name, "type": "sql"})

            # Cassandra: CREATE KEYSPACE keyspacename
            elif "create keyspace" in lower_line:
                parts = lower_line.replace(";", " ").split("create keyspace")
                if len(parts) > 1:
                    name = parts[1].strip().split()[0]
                    cdb_statements.append({"name": name, "type": "nosql (cassandra)"})

            # MongoDB: use dbname
            elif lower_line.startswith("use "):
                name = lower_line.split("use")[1].strip().split()[0]
                cdb_statements.append({"name": name, "type": "nosql (mongodb)"})

            # Redis: SELECT 0
            elif lower_line.startswith("select "):
                index = lower_line.split("select")[1].strip().split()[0]
                cdb_statements.append({"name": f"redis_db_{index}", "type": "nosql (redis)"})


    unique = {(d['name'], d['type']) for d in cdb_statements}
    return [{"name": name, "type": typ} for name, typ in unique]

#####################################################
def list_top_level_folders(root_path):
    try:
        entries = os.listdir(root_path)
        folders = [
            entry for entry in entries
            if os.path.isdir(os.path.join(root_path, entry))
        ]
        return folders
    except FileNotFoundError:
        print(f"Path not found: {root_path}")
        return []

############################################################################

def extract_java_classes(root_path):
    class_names = []

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.java'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        java_code = file.read()
                        tree = javalang.parse.parse(java_code)

                        for type_decl in tree.types:
                            if isinstance(type_decl, javalang.tree.ClassDeclaration):
                                class_name = type_decl.name
                                full_class_path = os.path.relpath(file_path, root_path).replace(os.sep, '.').replace(
                                    '.java', '')
                                class_names.append((class_name, full_class_path))

                except Exception as e:
                    print(f"Error in {file_path}: {e}")

    return class_names

#######################################################################################
def allFeatures_method(MICROSERVICE_PATH):

    results = []


    for root, _, files in os.walk(MICROSERVICE_PATH):
        for file in files:
            if file.endswith('.java'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        code = f.read()
                        tree = javalang.parse.parse(code)
                        imports = [imp.path for imp in tree.imports]

                        for _, class_decl in tree.filter(javalang.tree.ClassDeclaration):
                            class_name = class_decl.name

                            for method in class_decl.methods:
                                method_name = method.name


                                return_type = method.return_type.name if method.return_type else 'void'

                                generic_return_types = []
                                if method.return_type and method.return_type.arguments:
                                    for arg in method.return_type.arguments:
                                        if hasattr(arg, 'type') and arg.type:
                                            generic_return_types.append(arg.type.name)

                                param_types = [param.type.name for param in method.parameters]

                                local_types = []
                                if method.body:
                                    for stmt in method.body:
                                        if isinstance(stmt, javalang.tree.LocalVariableDeclaration):
                                            local_type = stmt.type.name
                                            local_types.append(local_type)

                                results.append({
                                    'file': file,
                                    'class': class_name,
                                    'method': method_name,
                                    'return_type': return_type,
                                    'generic_return_types': generic_return_types,
                                    'param_types': param_types,
                                    'local_types': local_types
                                })

                    except Exception as e:
                        # print(f'Error parsing {file}: {e}')
                        continue
    return results


