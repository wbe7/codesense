from kfp import dsl
from kubernetes.client.models import V1EnvVar, V1SecretKeySelector
from kfp import kubernetes
from kfp.kubernetes import secret

# Импортируем наши модульные компоненты
from .repo_sync.component import sync_repo_op
from .dvc_sync.component import dvc_sync_op
from .indexing.component import indexing_op

@dsl.pipeline(
    name="code-indexing-pipeline",
    description="A pipeline to sync a code repository, pull DVC data, and run indexing."
)
def code_indexing_pipeline(
    repo_url: str = "https://github.com/wbe7/codesense.git",
    branch_name: str = "main",
    collection_name: str = "codesense-prod",
    batch_size: int = 4
):
    """A KFP pipeline that orchestrates the full indexing workflow."""

    # Имя PVC, который должен быть предварительно создан в кластере
    # и будет использоваться всеми компонентами для обмена данными.
    pvc_name = "codesense-data-pvc"

    # Директория на PVC, куда будет смонтирован том.
    # Важно: эта директория будет общей для всех шагов.
    mount_path = "/data"

    # Путь внутри общей директории, куда будет клонирован исходный код.
    source_code_path = f"{mount_path}/source"

    # =========================================================================
    # Шаг 1: Синхронизация Git-репозитория
    # =========================================================================
    sync_repo_task = sync_repo_op(
        repo_url=repo_url,
        branch_name=branch_name,
        target_dir=source_code_path
    )
    kubernetes.mount_pvc(
        task=sync_repo_task,
        pvc_name=pvc_name,
        mount_path=mount_path
    )

    # =========================================================================
    # Шаг 2: Синхронизация данных с помощью DVC
    # =========================================================================
    dvc_sync_task = dvc_sync_op(
        source_dir=source_code_path
    ).after(sync_repo_task) # Запускается после успешной синхронизации репозитория
    
    kubernetes.mount_pvc(
        task=dvc_sync_task,
        pvc_name=pvc_name,
        mount_path=mount_path
    )
    
    # Передаем креды для S3 из секрета k8s с именем 's3-credentials'
    # DVC автоматически использует эти переменные окружения.
    secret.use_secret_as_env(
        dvc_sync_task,
        secret_name="s3-credentials",
        secret_key_to_env={
            "AWS_ACCESS_KEY_ID": "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY": "AWS_SECRET_ACCESS_KEY",
            "DVC_REMOTE_URL": "DVC_REMOTE_URL",
        }
    )

    # =========================================================================
    # Шаг 3: Запуск индексации кода
    # =========================================================================
    indexing_task = indexing_op(
        collection_name=collection_name,
        batch_size=batch_size,
        source_code_path=source_code_path
    ).after(dvc_sync_task) # Запускается после успешной загрузки данных



    kubernetes.mount_pvc(
        task=indexing_task,
        pvc_name=pvc_name,
        mount_path=mount_path
    )

    # Передаем креды для Qdrant из секрета k8s с именем 'qdrant-credentials'
    secret.use_secret_as_env(
        indexing_task,
        secret_name="qdrant-credentials",
        secret_key_to_env={
            "QDRANT_API_KEY": "QDRANT_API_KEY",
            "QDRANT_URL": "QDRANT_URL",
            "QDRANT_CONNECTION_METHOD": "QDRANT_CONNECTION_METHOD",
            "QDRANT_PORT": "QDRANT_PORT",
            "QDRANT_USE_TLS": "QDRANT_USE_TLS",
        }
    )
    indexing_task.set_env_variable(name="PYTORCH_ALLOC_CONF", value="expandable_segments:True")
