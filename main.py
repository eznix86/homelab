import argparse
import subprocess
import os
import sys
import yaml
from docker_volumes import create_source_folder, delete_source_folders

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create source folders based on Docker stack files.')
    parser.add_argument('action', type=str, help='Action to perform: deploy or remove')
    parser.add_argument('stack_names', type=str, nargs='+', help='Name of the Docker stack')
    return parser.parse_args()

def check_stack_file(stack_name):
    """Check if the stack file exists."""
    stack_file = f"{stack_name}.stack.yml"
    if not os.path.exists(stack_file):
        print(f"Stack file not found: {stack_file}")
        sys.exit(1)
    print (f"Stack file found: {stack_file}")
    return stack_file

def deploy_stack(stack_file, stack_name):
    """Deploy the Docker stack file."""
    print(f"Deploying stack: {stack_file}")
    # docker stack deploy -c stack_file stack_name
    subprocess.run(['docker', 'stack', 'deploy', '--detach=false', '-c', stack_file, stack_name])

def remove_stack(stack_name):
    """Remove the Docker stack."""
    print(f"Removing stack: {stack_name}")
    # docker stack rm stack_name
    subprocess.run(['docker', 'stack', 'rm', stack_name])

def create_file(file_name):
    with open(file_name, 'w') as f:
        f.write('')

def copy_file(source, destination):
    with open(source, 'r') as f:
        with open(destination, 'w') as f1:
            for line in f:
                f1.write(line)

"""
Check for
  x-custom:
    touch:
      - /var/data/filebrowser/database/filebrowser.db
    files:
      - .filebrowser.json:/var/data/filebrowser/config/filebrowser.json
  for services
"""
def read_yaml_file(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def process_custom(custom, stack_name):
    if 'touch' in custom:
        handle_touch_command(custom['touch'], stack_name)
    if 'files' in custom:
        handle_files_command(custom['files'], stack_name)

def handle_touch_command(files, stack_name):
    for file in files:
        create_file(file)
        print(f"Created file: {file}")

def handle_files_command(files, stack_name):
    for file in files:
        source, destination = file.split(':')
        copy_file(f"./{stack_name}/{source}", destination)
        print(f"Copied file: {source} to {destination}")

def check_custom_files(stack_file):
    data = read_yaml_file(stack_file)
    if 'x-custom' not in data:
        return
    custom = data['x-custom']
    process_custom(custom, stack_name)


if __name__ == "__main__":

    # python main.py deploy my_mystack mystack2 mystack3
    # python main.py remove my_mystack mystack2 mystack3
    # python main.py remove my_mystack
    # python main.py deploy all
    # python main.py remove all
    args = parse_args()
    stack_names = args.stack_names
    action = args.action

    match (action):
        case 'deploy':
            for stack_name in stack_names:
                print('Deploying stack:', stack_name)
                stack_file = check_stack_file(stack_name)
                create_source_folder(stack_file)
                check_custom_files(stack_file)
                deploy_stack(stack_file, stack_name)
        case 'remove':
            for stack_name in stack_names:
                print('Removing stack:', stack_name)
                remove_stack(stack_name)
                stack_file = check_stack_file(stack_name)
                delete_source_folders(stack_file)
        case _:
            print('Invalid action:', action)
            sys.exit(1)



