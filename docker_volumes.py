import os
import yaml
import glob
import re

IGNORE_PATHS = [
    '/var/lib/docker',
    '/var/lib/docker/volumes'
]

IGNORE_REGEX = [
    r'^/var/run/.*\.sock$',  # Matches /var/run/*.sock
    r'^/etc/.*$',            # Matches anything under /etc
    r'.*Caddyfile.*'         # Matches any file with Caddyfile in the name
]

DELETE_IGNORE_PATHS = [
    '/storage',
    '/var/lib/docker',
    '/var/lib/docker/volumes'
]

DELETE_IGNORE_REGEX = [
    r'^/storage.*$',  # Matches /storage*
    r'^/var/run/.*\.sock$',  # Matches /var/run/*.sock
    r'^/etc/.*$',            # Matches anything under /etc
]

def load_yaml_files():
    """Load all YAML files in the current directory."""
    yaml_files = glob.glob('*.yaml') + glob.glob('*.yml')
    return yaml_files

def read_yaml_file(file_path):
    """Read a YAML file and return its content."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def should_ignore_path(path):
    """Check if a path should be ignored based on predefined paths or regex."""
    if path in IGNORE_PATHS:
        return True
    for regex in IGNORE_REGEX:
        if re.match(regex, path):
            return True
    return False

def create_folder_if_not_exists(path):
    """Create a folder if it does not exist, ignoring specified paths or regex."""
    print('Creating folder:', path)
    if should_ignore_path(path):
        print(f"Ignoring path: {path}")
        return

    # Check if the path contains a dot (.) but is not a file extension
    if '.' in os.path.basename(path) \
        and not os.path.basename(path).startswith('.'):

        previous_path = path
        path = os.path.dirname(path)
        print(f"Creating directory {path} without dot (.) instead: {previous_path}")

    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created folder: {path}")
    else:
        print(f"Folder already exists: {path}")

def process_volumes(volumes):
    """Process the volumes to create source folders."""
    for volume in volumes:
        if isinstance(volume, str):
            source, _ = volume.split(':', 1)
            if source.startswith('/'):
                create_folder_if_not_exists(source)
        elif isinstance(volume, dict) and volume.get('type') == 'bind':
            create_folder_if_not_exists(volume.get('source'))

def process_services(services):
    """Process services in the YAML data to handle volumes."""
    for service_data in services.values():
        volumes = service_data.get('volumes', [])
        process_volumes(volumes)

def create_source_folder(yaml_file):
    """Create source folders based on the volumes in the YAML file."""
    data = read_yaml_file(yaml_file)
    if 'services' in data:
        process_services(data['services'])

def create_source_folders(yaml_files):
    """Create source folders based on the volumes in the YAML files."""
    for yaml_file in yaml_files:
        create_source_folder(yaml_file)


def should_delete_ignore_path(path):
    """Check if a path should be ignored based on predefined paths or regex."""
    if path in DELETE_IGNORE_PATHS:
        return True
    for regex in DELETE_IGNORE_REGEX:
        if re.match(regex, path):
            return True
    return False

def delete_folder_if_exists(path):
    """Delete a folder if it exists, ignoring specified paths or regex."""
    print('Deleting folder:', path)
    if should_delete_ignore_path(path):
        print(f"Ignoring path: {path}")
        return

    if os.path.exists(path):
        try:
            os.rmdir(path)
        except NotADirectoryError as e:
            print(f"Error deleting folder: {path}")
            print(e)
            if input(f"Delete file forcefully? {path} (y/n): ").lower() == 'y':
                os.remove(path)
        except OSError as e:
            print(f"Error deleting folder: {path}")
            print(e)
            if input(f"Delete folder forcefully? {path} (y/n): ").lower() == 'y':
                import shutil
                shutil.rmtree(path)
        print(f"Deleted folder: {path}")
    else:
        print(f"Folder does not exist: {path}")

def process_delete_folders(services):
    """Process services in the YAML data to handle volumes."""
    for service_data in services.values():
        volumes = service_data.get('volumes', [])
        for volume in volumes:
            if isinstance(volume, str):
                source, _ = volume.split(':', 1)
                if source.startswith('/'):
                    delete_folder_if_exists(source)
            elif isinstance(volume, dict) and volume.get('type') == 'bind':
                delete_folder_if_exists(volume.get('source'))

def delete_source_folders(yaml_file):
    """Delete source folders based on the volumes in the YAML files."""
    data = read_yaml_file(yaml_file)
    if 'services' in data:
        process_delete_folders(data['services'])




if __name__ == "__main__":
    yaml_files = load_yaml_files()
    create_source_folders(yaml_files)
