import yaml
import subprocess
import os
import shutil
import sys

# Пакет 'codesense' был установлен через 'pip install -e .',
# поэтому мы можем импортировать его напрямую.
from codesense.utils.url_parser import parse_repository_info

# Обновленные константы
YAML_CONFIG_FILE = "codesense.yaml"
DATA_DIR = "data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

VENV_DVC = os.path.join(".venv", "bin", "dvc")

def run_command(command, cwd=None, check=True):
    """Helper to run shell commands."""
    if command[0] == "dvc":
        command[0] = VENV_DVC
    
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result

def main():
    # 1. Убедимся, что директория для сырых данных существует
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # 2. Чтение репозиториев из главного конфига
    with open(YAML_CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    repositories = config.get('repositories', [])

    # 3. Обработка каждого репозитория
    for repo_url in repositories:
        try:
            info = parse_repository_info(repo_url)
            target_repo_path = os.path.join(RAW_DATA_DIR, info['id'])
            
            print(f"Processing repository: {repo_url}")

            # 3.1. Удаление существующей директории для обеспечения свежести
            if os.path.exists(target_repo_path):
                print(f"  Removing existing directory to re-clone: {target_repo_path}")
                shutil.rmtree(target_repo_path)

            # 3.2. Клонирование репозитория
            print(f"  Cloning into: {target_repo_path}")
            os.makedirs(os.path.dirname(target_repo_path), exist_ok=True)
            run_command(["git", "clone", "--depth", "1", repo_url, target_repo_path])
            
            # 3.3. Удаление .git директории
            git_dir = os.path.join(target_repo_path, ".git")
            if os.path.exists(git_dir):
                print(f"  Removing .git directory...")
                shutil.rmtree(git_dir)

        except Exception as e:
            print(f"Error processing {repo_url}: {e}")

    # 4. Добавление всех сырых данных в DVC
    print(f"Adding {RAW_DATA_DIR} to DVC...")
    run_command(["dvc", "add", RAW_DATA_DIR])

    # 5. Коммит и пуш в удаленное хранилище
    print("Staging and committing new DVC data to Git...")
    run_command(["git", "add", f"{RAW_DATA_DIR}.dvc", ".gitignore"])
    
    commit_successful = False
    try:
        # Вызываем с check=False, чтобы обработать случай "nothing to commit"
        commit_result = run_command(["git", "commit", "-m", "Update raw codebases dataset"], check=False)
        if commit_result.returncode == 0:
            print("Git commit successful.")
            commit_successful = True
        elif "nothing to commit" in commit_result.stdout or "nothing to commit" in commit_result.stderr:
            print("No changes to commit to Git.")
        else:
            # Если есть другая ошибка коммита, выводим ее и падаем
            print(f"Git commit failed with exit code {commit_result.returncode}.")
            raise subprocess.CalledProcessError(commit_result.returncode, commit_result.args, output=commit_result.stdout, stderr=commit_result.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during git commit: {e}")
        raise

    if commit_successful:
        print("Pushing DVC cache to remote...")
        run_command(["dvc", "push"])
    else:
        print("Skipping DVC push as no Git commit was made.")

if __name__ == "__main__":
    main()