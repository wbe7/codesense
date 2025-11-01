# Развертывание Langfuse

## Развертывание

1.  Добавьте репозиторий Langfuse:

    ```bash
    helm repo add langfuse https://langfuse.github.io/langfuse-k8s
    helm repo update
    ```

2.  Для развертывания или обновления Langfuse выполните следующую команду из директории `infra/langfuse`:

    ```bash
    helm upgrade -i langfuse langfuse/langfuse -n langfuse -f values.yaml --create-namespace
    ```

## Устранение проблем с миграциями

Если под `langfuse-web` находится в состоянии `CrashLoopBackOff` из-за проблем с миграциями, выполните следующие шаги:

1.  **Запустите временный "ремонтный" под `langfuse-repair-pod`:**
    Используйте уже созданный файл `infra/langfuse/repair-pod.yaml`.
    ```bash
    kubectl apply -f infra/langfuse/repair-pod.yaml
    ```
    Убедитесь, что под перешел в состояние `Running`.

2.  **Определите проблемную миграцию:**
    *   **Для PostgreSQL (Prisma):** Посмотрите логи пода `langfuse-web`. Ошибка `Error: P3009` укажет на имя проблемной миграции (например, `20250214173309_add_timescope_to_configs`).
    *   **Для ClickHouse:** Посмотрите логи пода `langfuse-web`. Ошибка `Dirty database version X` или `Table default.<имя_таблицы> already exists.` укажет на номер проблемной версии (например, `24`).

3.  **"Откатите" или "форсируйте" миграцию:**

    *   **Для PostgreSQL (Prisma):** Если миграция упала, но не внесла изменений в схему, используйте `--rolled-back`. Если миграция внесла частичные изменения (например, создала столбец, но не завершилась), используйте `--applied`.
        ```bash
        kubectl exec langfuse-repair-pod -n langfuse -- npx prisma migrate resolve --rolled-back <имя_проблемной_миграции> --schema=./packages/shared/prisma/schema.prisma
        # или
        kubectl exec langfuse-repair-pod -n langfuse -- npx prisma migrate resolve --applied <имя_проблемной_миграции> --schema=./packages/shared/prisma/schema.prisma
        ```

    *   **Для ClickHouse:**
        Если ошибка `Dirty database version X`, то "форсируйте" до `X-1`.
        Если ошибка `Table default.<имя_таблицы> already exists.`, то "форсируйте" до версии, которая пытается создать эту таблицу.

        ```bash
        kubectl exec langfuse-repair-pod -n langfuse -- sh -c 'migrate -path packages/shared/clickhouse/migrations/unclustered -database "clickhouse://default:$CLICKHOUSE_PASSWORD@langfuse-clickhouse:9000/default?username=$CLICKHOUSE_USER&password=$CLICKHOUSE_PASSWORD&database=$CLICKHOUSE_DB&x-multi-statement=true&x-migrations-table-engine=MergeTree" force <номер_версии>'
        ```
        **Важно:** Переменные окружения `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DB` должны быть установлены в `langfuse-repair-pod` и содержать правильные значения.

4.  **Удалите основной под `langfuse-web`:**
    ```bash
    kubectl delete pod <имя_пода_langfuse-web> -n langfuse
    ```
    (Kubernetes автоматически создаст новый под, который применит миграции заново).

5.  **Удалите "ремонтный" под `langfuse-repair-pod`:**
    ```bash
    kubectl delete pod langfuse-repair-pod -n langfuse
    ```