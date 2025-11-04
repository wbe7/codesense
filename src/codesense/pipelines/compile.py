import kfp
from .pipeline import code_indexing_pipeline

if __name__ == "__main__":
    # Instantiate the KFP compiler
    compiler = kfp.compiler.Compiler()

    # Compile the pipeline function into a YAML file
    compiler.compile(
        pipeline_func=code_indexing_pipeline,
        package_path="pipeline.yaml",
    )

    print("Pipeline compiled successfully to pipeline.yaml")
