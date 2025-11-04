from kfp import dsl

@dsl.container_component
def dvc_sync_op(source_dir: str = "/data/source"):
    """
    An idempotent KFP component to pull DVC data.

    It runs `dvc pull` in the specified source directory.
    This command is idempotent and will only download changes.
    """
    return dsl.ContainerSpec(
        # Using our main image which has dvc installed
        image='wbe7/codesense:latest',
        command=[
            "sh",
            "-c",
            f'''
                set -e
                echo "Syncing DVC data in {source_dir}"
                
                cd {source_dir}
                dvc pull
                
                echo "DVC sync complete."
            '''
        ]
    )
