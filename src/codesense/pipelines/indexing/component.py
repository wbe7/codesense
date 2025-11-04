from kfp import dsl

@dsl.container_component
def indexing_op(collection_name: str, batch_size: int, source_code_path: str):
    """
    KFP component to run the code indexing pipeline.

    This component loads code from DVC, processes it, creates embeddings,
    and uploads them to a Qdrant collection.
    """
    return dsl.ContainerSpec(
        image='wbe7/codesense:latest',
        command=[
            "sh",
            "-c",
            f'''
                set -e
                echo "Running indexing from {source_code_path}"
                cd {source_code_path} && \
                python -m codesense.pipelines.indexing.run \
                    --collection-name "{collection_name}" \
                    --batch-size {batch_size}
            '''
        ],
    )
