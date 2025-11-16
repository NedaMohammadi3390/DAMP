import os
import re
import json

http_mappings = {
    "GET": r"@GetMapping\b|@RequestMapping\s*\([^\)]*method\s*=\s*RequestMethod\.GET",
    "POST": r"@PostMapping\b|@RequestMapping\s*\([^\)]*method\s*=\s*RequestMethod\.POST",
    "PUT": r"@PutMapping\b|@RequestMapping\s*\([^\)]*method\s*=\s*RequestMethod\.PUT",
    "DELETE": r"@DeleteMapping\b|@RequestMapping\s*\([^\)]*method\s*=\s*RequestMethod\.DELETE",
    "PATCH": r"@PatchMapping\b|@RequestMapping\s*\([^\)]*method\s*=\s*RequestMethod\.PATCH"
}

def find_api_methods(root_dir):
    api_list = []

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".java"):
                file_path = os.path.join(dirpath, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                    for i, line in enumerate(lines):
                        for method, pattern in http_mappings.items():
                            if re.search(pattern, line):
                                api_list.append({
                                    "file": file_path,
                                    "line": i + 1,
                                    "method": method,
                                    "code": line.strip()
                                })
    return api_list
