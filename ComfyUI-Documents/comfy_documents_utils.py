import os
from typing import List

def get_input_directory():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), "input")

def get_supported_extensions():
    return [".pdf", ".txt", ".doc", ".docx"]

def get_filename_list() -> List[str]:
    input_dir = get_input_directory()
    extensions = get_supported_extensions()
    
    files = []
    for file in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, file)):
            _, ext = os.path.splitext(file)
            if ext.lower() in extensions:
                files.append(file)
    
    return sorted(files)