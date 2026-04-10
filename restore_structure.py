import os
import shutil

repo_root = "/Users/balajik/auto -dealer"
app_root = os.path.join(repo_root, "automobile_dealership")
package_root = os.path.join(app_root, "automobile_dealership")
module_root = os.path.join(package_root, "automobile_dealership")

# 1. Create Level 3 module folder
if not os.path.exists(module_root):
    print(f"Creating {module_root}")
    os.makedirs(module_root)
    with open(os.path.join(module_root, "__init__.py"), "w") as f:
        pass

# 2. Components to move to Level 3 (from Level 2)
components = [
    "api", "doctype", "events", "fixtures", "module_def", 
    "overrides", "page", "patches", "print_format", 
    "report", "setup", "tasks.py", "tests", "fix_db.py"
]

for item in components:
    src = os.path.join(package_root, item)
    dest = os.path.join(module_root, item)
    if os.path.exists(src):
        print(f"Moving {src} to {dest}")
        if os.path.isdir(src):
            # Check if destination directory exists, if so merge or move
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.move(src, dest)
        else:
            shutil.move(src, dest)

# 3. Move hooks.py and modules.txt to Level 2 (from Level 1)
misc_to_package = ["hooks.py", "modules.txt", "requirements.txt"] # requirements.txt might be in root though
for item in ["hooks.py", "modules.txt"]:
    src = os.path.join(app_root, item)
    dest = os.path.join(package_root, item)
    if os.path.exists(src):
        print(f"Moving {src} to {dest}")
        shutil.move(src, dest)

print("Restoration script finished.")
