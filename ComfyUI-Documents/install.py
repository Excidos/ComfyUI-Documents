import subprocess
import sys
import os

def install_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Successfully installed requirements for ComfyUI-Documents")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        
if __name__ == "__main__":
    install_requirements()