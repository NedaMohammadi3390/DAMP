import os
import json
import extract_deps
def extract(system):
    depen = []
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependencies.json")

    extract_deps.extract_dependencies(system, script_dir)
    with open(script_dir) as f:
        data = json.load(f)
        for dep in data:
            dep_type = dep.get("type", "")
            artifact = dep.get("artifact", "")
            if dep_type and artifact:
                depen.append(artifact)
    return depen
