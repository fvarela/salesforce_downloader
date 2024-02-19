import os

def create_file_if_not_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("")

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def create_nested_folders_if_not_exists(path):
    directory_path, file_name = os.path.split(path)
    target_path = directory_path if file_name else path
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    else:
        pass