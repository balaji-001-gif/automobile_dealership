import os
import json

repo_root = "/Users/balajik/auto -dealer"
doctype_dir = os.path.join(repo_root, "automobile_dealership", "automobile_dealership", "doctype")

if not os.path.exists(doctype_dir):
    print(f"Error: DocType directory not found at {doctype_dir}")
    exit(1)

for folder in os.listdir(doctype_dir):
    folder_path = os.path.join(doctype_dir, folder)
    if os.path.isdir(folder_path):
        # Look for .json file to get the DocType name
        json_file = os.path.join(folder_path, f"{folder}.json")
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                data = json.load(f)
                doctype_name = data.get("name")
            
            js_file = os.path.join(folder_path, f"{folder}.js")
            if not os.path.exists(js_file):
                print(f"Creating {js_file} for {doctype_name}")
                with open(js_file, "w") as f:
                    content = f"""// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on("{doctype_name}", {{
	// refresh(frm) {{

	// }}
}});
"""
                    f.write(content)

print("JS Generation finished.")
