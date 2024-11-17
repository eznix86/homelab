import argparse
import subprocess
import os
import sys
from typing import List, Dict, Any
import yaml
from docker_volumes import create_source_folder, delete_source_folders


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Manage Docker stacks with custom pre-deployment steps.")
    parser.add_argument("action", choices=["deploy", "remove"], help="Action to perform: deploy or remove")
    parser.add_argument("stack_names", nargs="+", help="Name(s) of the Docker stack(s) or 'all'")
    return parser.parse_args()


def check_stack_file(stack_name: str) -> str:
    """Ensure the stack file exists."""
    stack_file = f"{stack_name}.stack.yml"
    if not os.path.exists(stack_file):
        raise FileNotFoundError(f"Stack file not found: {stack_file}")
    print(f"Stack file found: {stack_file}")
    return stack_file


def deploy_stack(stack_file: str, stack_name: str) -> None:
    """Deploy a Docker stack."""
    print(f"Deploying stack: {stack_file}")
    subprocess.run(
        ["docker", "stack", "deploy", "--detach=false", "-c", stack_file, stack_name],
        check=True
    )


def remove_stack(stack_name: str) -> None:
    """Remove a Docker stack."""
    print(f"Removing stack: {stack_name}")
    subprocess.run(["docker", "stack", "rm", stack_name], check=True)


def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """Read a YAML file."""
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise ValueError(f"Error reading YAML file {file_path}: {e}")


def handle_touch_command(files: List[str]) -> None:
    """Create empty files."""
    for file in files:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            pass
        print(f"Created file: {file}")


def handle_files_command(files: List[str], stack_name: str) -> None:
    """Copy files from source to destination."""
    for mapping in files:
        try:
            source, destination = mapping.split(":")
            full_source_path = os.path.join(stack_name, source)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(full_source_path, "r") as src, open(destination, "w") as dest:
                dest.write(src.read())
            print(f"Copied file: {full_source_path} to {destination}")
        except ValueError:
            raise ValueError(f"Invalid file mapping format: {mapping}")


def process_custom(custom: Dict[str, Any], stack_name: str) -> None:
    """Process custom directives from the stack file."""
    if "touch" in custom:
        handle_touch_command(custom["touch"])
    if "files" in custom:
        handle_files_command(custom["files"], stack_name)


def check_custom_files(stack_file: str, stack_name: str) -> None:
    """Check for and process custom directives in the stack file."""
    data = read_yaml_file(stack_file)
    custom = data.get("x-custom")
    if custom:
        process_custom(custom, stack_name)


def process_stacks(action: str, stack_names: List[str]) -> None:
    """Process stacks based on the action."""
    for stack_name in stack_names:
        try:
            print(f"{action.capitalize()}ing stack: {stack_name}")
            stack_file = check_stack_file(stack_name)

            if action == "deploy":
                create_source_folder(stack_file)
                check_custom_files(stack_file, stack_name)
                deploy_stack(stack_file, stack_name)
            elif action == "remove":
                remove_stack(stack_name)
                delete_source_folders(stack_file)
        except Exception as e:
            print(f"Error while processing stack '{stack_name}': {e}")
            continue


def main() -> None:
    """Main function."""
    args = parse_args()
    action = args.action
    stack_names = args.stack_names

    if "all" in stack_names:
        stack_names = [
            f[:-10] for f in os.listdir(".") if f.endswith(".stack.yml")
        ]  # Extract stack names from available `.stack.yml` files

    process_stacks(action, stack_names)


if __name__ == "__main__":
    main()
