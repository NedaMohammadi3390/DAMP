import argparse
import os
import json
import xml.etree.ElementTree as ET

def extract_maven_dependencies(project_path):
    deps = []
    pom_path = os.path.join(project_path, "pom.xml")
    if os.path.exists(pom_path):
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            for dep in root.findall('.//m:dependency', ns):

                group_id = dep.find('m:groupId', ns)
                artifact_id = dep.find('m:artifactId', ns)
                version = dep.find('m:version', ns)
                deps.append({
                    "type": "maven",
                    "group": group_id.text if group_id is not None else "",
                    "artifact": artifact_id.text if artifact_id is not None else "",
                    "version": version.text if version is not None else ""
                })
        except Exception as e:
            print(f"[!] Error in reading file pom.xml: {e}")
    return deps



def extract_gradle_dependencies(project_path):
    deps = []
    gradle_file = os.path.join(project_path, "build.gradle")
    if not os.path.exists(gradle_file):
        return deps

    try:
        with open(gradle_file, "r") as f:
            content = f.read()

        dep_block_pattern = r'dependencies\s*\{(.*?)\}'
        matches = re.findall(dep_block_pattern, content, re.DOTALL)

        if not matches:
            return deps

        for block in matches:
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                pattern = r'^(implementation|compile|testCompile|classpath|compileOnly|annotationProcessor|testImplementation|testCompileOnly|testAnnotationProcessor)\s*(?:\(\s*)?[\'"]([\w\.\-]+):([\w\.\-]+)(?::([\w\.\-${}]+))?[\'"]\s*(?:\))?'

                match = re.match(pattern, line)
                if match:
                    dep = {
                        "type": "gradle",
                        "scope": match.group(1),
                        "group": match.group(2),
                        "artifact": match.group(3),
                        "version": match.group(4) if match.group(4) else ""
                    }
                    deps.append(dep)

    except Exception as e:
        print(f"[!] Error reading build.gradle: {e}")

    return deps

def extract_gradle_dependencies2(project_path):
    deps = []
    gradle_file = os.path.join(project_path, "build.gradle")
    if os.path.exists(gradle_file):
        try:
            with open(gradle_file, "r") as f:
                for line in f:
                    line = line.strip()
                    pattern = r'(implementation|compile|testCompile|classpath)\((["\'])([\w\.\-]+):([\w\.\-]+)(:([\w\.\-${}]+))?\2\)'
                    match = re.search(pattern, line)
                    if match:
                        dep = {
                            "type": "gradle",
                            "scope": match.group(1),
                            "group": match.group(3),
                            "artifact": match.group(4),
                            "version": match.group(6) if match.group(6) else ""
                        }
                        deps.append(dep)
        except Exception as e:
            print(f"[!] error in reading file build.gradle: {e}")
    return deps


def extract_dependencies(project_path, output_path):

    all_deps = extract_maven_dependencies(project_path) + extract_gradle_dependencies(project_path)+ extract_gradle_dependencies2(project_path)
    with open(output_path, "w") as out:
        json.dump(all_deps, out, indent=4)
    print(f"[✓] dependencies are saved in the '{output_path} file!")
