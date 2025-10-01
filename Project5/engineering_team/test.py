import subprocess
try:
    subprocess.run(['docker', '--version'], check=True, capture_output=True)
    print("Docker command was found successfully.")
except FileNotFoundError as e:
    print(f"Error: Docker command not found. {e}")
