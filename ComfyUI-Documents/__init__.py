import os
import subprocess
import sys
from .document_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from .utils import folder_paths
from .server import WEB_DIRECTORY

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

def install_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Successfully installed requirements for ComfyUI-Documents")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Attempting to install required packages for ComfyUI-Documents...")
    install_requirements()
    import fitz

# Ensure the input directory exists
input_dir = folder_paths.get_input_directory()
os.makedirs(input_dir, exist_ok=True)

# Set up the web directory for the JavaScript file
javascript_file = os.path.join(WEB_DIRECTORY, "js", "documents.core.js")

if os.path.exists(javascript_file):
    print(f"documents.core.js found at {javascript_file}")
else:
    print(f"Warning: documents.core.js not found at {javascript_file}")

def get_javascript():
    if os.path.exists(javascript_file):
        with open(javascript_file, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return ""

__all__.extend(["get_javascript"])