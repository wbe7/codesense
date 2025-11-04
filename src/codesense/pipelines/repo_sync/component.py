from kfp import dsl

@dsl.container_component
def sync_repo_op(repo_url: str, branch_name: str, target_dir: str = "/data/source"):
    """
    An idempotent KFP component to clone or sync a git repository.

    If the target directory is empty, it clones the repository.
    If the repository already exists, it fetches the latest changes and
    resets the branch to match the remote.
    """
    return dsl.ContainerSpec(
        # Using a lightweight image with just git
        image='alpine/git:latest',
        command=[
            "sh",
            "-c",
            # Using a multi-line script for clarity.
            # The script is designed to be idempotent.
            f'''
                set -e
                echo "Syncing repository {repo_url} to {target_dir}"
                
                mkdir -p {target_dir}
                cd {target_dir}
                
                if [ -d ".git" ]; then
                    echo "Repository exists, syncing..."
                    git remote set-url origin {repo_url}
                    git fetch origin
                    git checkout {branch_name}
                    git reset --hard origin/{branch_name}
                else
                    echo "Repository does not exist, cloning..."
                    # For private repos, the token should be included in the repo_url
                    # e.g., https://oauth2:<TOKEN>@github.com/user/repo.git
                    git clone --branch {branch_name} {repo_url} .
                fi
                
                echo "Sync complete."
            '''
        ]
    )
