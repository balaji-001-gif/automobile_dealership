import os
import shutil

repo_root = "/Users/balajik/auto -dealer"
level1 = os.path.join(repo_root, "automobile_dealership")
level2 = os.path.join(level1, "automobile_dealership")
level3 = os.path.join(level2, "automobile_dealership")

# 1. Bring components from Level 3 to Level 2
if os.path.exists(level3):
    print(f"Flattening {level3} into {level2}")
    for item in os.listdir(level3):
        src = os.path.join(level3, item)
        dest = os.path.join(level2, item)
        if item == "__init__.py":
            # Just ensureLevel 2 has it
            if not os.path.exists(dest):
                shutil.copy2(src, dest)
            os.remove(src)
            continue
            
        print(f"Moving {src} to {dest}")
        if os.path.exists(dest):
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            else:
                os.remove(dest)
        shutil.move(src, dest)
    
    # Remove empty Level 3
    print(f"Removing {level3}")
    os.rmdir(level3)

# 2. Bring hooks and modules from Level 2 to Level 1
to_level1 = ["hooks.py", "modules.txt", "workspace"]
for item in to_level1:
    src = os.path.join(level2, item)
    dest = os.path.join(level1, item)
    if os.path.exists(src):
        print(f"Moving {src} to {dest}")
        if os.path.exists(dest):
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            else:
                os.remove(dest)
        shutil.move(src, dest)

# 3. Ensure __init__.py in Level 1 and Level 2
for folder in [level1, level2]:
    init_path = os.path.join(folder, "__init__.py")
    if not os.path.exists(init_path):
        print(f"Creating {init_path}")
        with open(init_path, "w") as f:
            f.write('__version__ = "1.0.0"\n' if folder == level1 else "")

print("Final cleanup finished.")
