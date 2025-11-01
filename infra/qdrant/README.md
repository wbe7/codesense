# Развертывание Qdrant

## Развертывание

1.  Добавьте репозиторий Qdrant:

    ```bash
    helm repo add qdrant https://qdrant.to/helm
    ```

2.  Для развертывания или обновления Qdrant выполните следующую команду из директории `infra/qdrant`:

    ```bash
    helm upgrade -i qdrant qdrant/qdrant -n qdrant -f values.yaml --create-namespace
    ```
