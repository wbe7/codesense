import yaml
import subprocess
import os
import shutil
import re

CODEBASES_DIR = "codebases"
YAML_CONFIG_FILE = os.path.join(CODEBASES_DIR, "codebases.yaml")

# Path to the virtual environment's executables
VENV_PYTHON = os.path.join(".venv", "bin", "python")
VENV_DVC = os.path.join(".venv", "bin", "dvc")

def run_command(command, cwd=None, check=True):
    """Helper to run shell commands, using venv executables for dvc."""
    # Prepend venv executable for dvc commands
    if command[0] == "dvc":
        command[0] = VENV_DVC
    elif command[0] == "python":
        command[0] = VENV_PYTHON

    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result

def parse_repo_url(repo_url):
    """Parses a Git repository URL to extract host, organization, and repository name."""
    # Regex to match common Git URL formats (HTTPS and SSH)
    match = re.match(r"(?:https?://|git@)([^:/]+)[/:]([^/]+)/([^/.]+)(?:\.git)?", repo_url)
    if not match:
        raise ValueError(f"Could not parse repository URL: {repo_url}")

    host = match.group(1)
    org = match.group(2)
    repo_name = match.group(3)
    return host, org, repo_name

def main():
    # Ensure the codebases directory exists
    os.makedirs(CODEBASES_DIR, exist_ok=True)

    # Read repositories from codebases.yaml
    with open(YAML_CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    repositories = config.get('repositories', [])

    for repo_url in repositories:
        try:
            host, org, repo_name = parse_repo_url(repo_url)
            target_repo_path = os.path.join(CODEBASES_DIR, host, org, repo_name)
            dvc_file_path = target_repo_path + ".dvc"

            print(f"Processing repository: {repo_url}")
            print(f"  Target path: {target_repo_path}")

            # 1. Remove existing DVC tracking and directory if it exists
            if os.path.exists(dvc_file_path):
                print(f"  Removing existing DVC tracking file: {dvc_file_path}")
                run_command(["dvc", "remove", dvc_file_path])
            
            if os.path.exists(target_repo_path):
                print(f"  Removing existing repository directory: {target_repo_path}")
                shutil.rmtree(target_repo_path)
            
            # Ensure parent directories exist for the target repo path
            os.makedirs(os.path.dirname(target_repo_path), exist_ok=True)

            # 2. Clone the repository
            print(f"  Cloning {repo_url} into {target_repo_path}...")
            run_command(["git", "clone", repo_url, target_repo_path])

            # 3. Delete the .git directory
            git_dir = os.path.join(target_repo_path, ".git")
            if os.path.exists(git_dir):
                print(f"  Removing .git directory from {target_repo_path}...")
                shutil.rmtree(git_dir)
            
            # 4. Add to DVC
            print(f"  Adding {target_repo_path} to DVC...")
            run_command(["dvc", "add", target_repo_path])

        except Exception as e:
            print(f"Error processing {repo_url}: {e}")
            # Continue to next repository even if one fails

    # 5. Stage and commit updated .dvc files to Git
    print("Staging and committing updated .dvc files to Git...")
    run_command(["git", "add", CODEBASES_DIR]) # Add the whole codebases directory to catch all .dvc files
    
    try:
        run_command(["git", "commit", "-m", "Update RAG codebases via repositories-converge.py"])
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr:
            print("No changes to commit.")
        else:
            raise

    # 6. Push DVC cache to remote (optional, but good practice)
    print("Pushing DVC cache to remote...")
    run_command(["dvc", "push"])

if __name__ == "__main__":
    main()