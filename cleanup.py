import os
import json
import re

def rename_parent_dir_if_metadata_exists(base_path, rename_func):
    for root, dirs, files in os.walk(base_path):
        if 'metaData.json' in files:
            # root is the path to the directory containing metaData.json
            parent_dir_path = root
            parent_dir_name = os.path.basename(parent_dir_path)
            grandparent_dir = os.path.dirname(parent_dir_path)
            data = None
            with open(os.path.join(parent_dir_path, files[0]), 'r', encoding='utf-8') as metaData:
                input = metaData.read()
                data = json.loads(input)

            # change and write the new format
            data["委員發言時間"] = data["委員發言時間"].replace(':', '').replace(' ', '')
            with open(os.path.join(parent_dir_path, files[0]), 'w', encoding='utf-8') as new_metaData:
                json.dump(data, new_metaData, ensure_ascii=False, indent=4)

            suffix = re.match(r'(\d{6})-(\d{6})', data["委員發言時間"])[1]
            new_dir_name = rename_func(parent_dir_name, suffix)
            new_dir_path = os.path.join(grandparent_dir, new_dir_name)

            if new_dir_path != parent_dir_path:
                print(f"Renaming: {parent_dir_path} -> {new_dir_path}")
                os.rename(parent_dir_path, new_dir_path)

            # Prevent os.walk from descending into renamed dirs
            dirs.clear()

# Match trailing "000821" pattern and renamed into "suffix"
def example_rename(dirname, suffix):
    match = re.match(r'(.+_)(\d{6})$', dirname)
    if match:
        prefix, old_id = match.groups()
        new_id = suffix
        new_dir_name = prefix + new_id
        print(new_dir_name)
    return new_dir_name

# Example usage
base_directory = "委員資料夾"
rename_parent_dir_if_metadata_exists(base_directory, example_rename)
