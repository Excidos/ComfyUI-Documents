import os

class folder_paths:
    @classmethod
    def get_input_directory(cls):
        # Update the path to the correct location of the 'input' directory
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), "input")

    @classmethod
    def get_annotated_filepath(cls, filename):
        input_dir = cls.get_input_directory()
        file_path = os.path.join(input_dir, filename)
        return file_path, input_dir

    @classmethod
    def exists_annotated_filepath(cls, filename):
        file_path, _ = cls.get_annotated_filepath(filename)
        return os.path.exists(file_path)

def strip_path(path):
    path = path.strip()
    if path.startswith("\""):
        path = path[1:]
    if path.endswith("\""):
        path = path[:-1]
    return path

def is_safe_path(path):
    if "STRICT_PATHS" not in os.environ:
        return True
    basedir = os.path.abspath('.')
    try:
        common_path = os.path.commonpath([basedir, path])
    except:
        return False
    return common_path == basedir