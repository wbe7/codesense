# Инструкция по установке NVIDIA GPU Operator

Этот документ содержит пошаговую инструкцию по установке и базовой настройке NVIDIA GPU Operator в кластере Kubernetes.

## Предварительные требования

- Рабочий кластер Kubernetes (например, Deckhouse).
- Установленный Helm CLI.
- GPU-ноды, подключенные к кластеру, с которых удалены все предыдущие установки драйверов NVIDIA (см. `../README.md`).

## Процесс установки

1.  **Подготовьте неймспейс `gpu-operator`:**
    -   Создайте неймспейс:
        ```bash
        kubectl create namespace gpu-operator
        ```
    -   **Важно:** Для корректной работы GPU Operator необходимо исключить его неймспейс из политики безопасности Deckhouse `d8-pod-security-baseline-deny-default`. Для этого примените лейбл `privileged` к неймспейсу:
        ```bash
        kubectl label ns gpu-operator security.deckhouse.io/pod-policy=privileged
        ```

2.  **Добавьте Helm-репозиторий NVIDIA:**
    ```bash
    helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
    helm repo update
    ```

3.  **Изучите и настройте `values.yaml`:**
    -   Скачайте оригинальный `values.yaml` для справки:
        ```bash
        helm show values nvidia/gpu-operator > ./original-values.yaml
        ```
    -   Создайте кастомный `values.yaml` (пример: `./values.yaml`), где вы определите конфигурации `devicePlugin` для `Time-Slicing` и `Exclusive` режимов. Пример содержимого `values.yaml`:
        ```yaml
        # Custom values for the NVIDIA GPU Operator

        devicePlugin:
          config:
            create: true
            name: "nvidia-device-plugin-configs"
            default: "exclusive-config"
            data:
              exclusive-config: |-
                version: v1
                flags:
                  migStrategy: none
              timeslicing-config: |-
                version: v1
                sharing:
                  timeSlicing:
                    resources:
                    - name: nvidia.com/gpu
                      replicas: 4
        ```

4.  **Установите GPU Operator:**
    ```bash
    helm upgrade -i gpu-operator nvidia/gpu-operator \
      --namespace gpu-operator \
      -f ./values.yaml
    ```

5.  **Настройте выбор конфигурации для нод (Time-Slicing/Exclusive):**
    -   В файле `../gpu-nodegroups.yaml` (или аналогичном, где определены ваши `NodeGroup` Deckhouse) добавьте лейбл `nvidia.com/device-plugin.config` в `nodeTemplate.labels` для каждой `NodeGroup`.
    -   Пример для `gpu-small` (Time-Slicing):
        ```yaml
        nodeTemplate:
          labels:
            gpu-type: small
            nvidia.com/device-plugin.config: timeslicing-config
          taints:
            - key: nvidia.com/gpu
              effect: NoSchedule
        ```
    -   Пример для `gpu-standard` (Exclusive):
        ```yaml
        nodeTemplate:
          labels:
            gpu-type: standard
            nvidia.com/device-plugin.config: exclusive-config
          taints:
            - key: nvidia.com/gpu
              effect: NoSchedule
        ```
    -   Примените обновленную конфигурацию `NodeGroup`:
        ```bash
        kubectl apply -f ../gpu-nodegroups.yaml
        ```

## Валидация

1.  **Проверьте поды оператора:**
    ```bash
    kubectl get pods -n gpu-operator -o wide
    ```
    Все поды должны быть в статусе `Running` или `Completed`.

2.  **Проверьте ресурсы GPU на ноде:**
    ```bash
    kubectl describe node <имя-вашей-gpu-ноды>
    ```
    В секциях `Capacity` и `Allocatable` должен появиться ресурс `nvidia.com/gpu` с соответствующим количеством.

3.  **Запустите тестовый CUDA Job:**
    Пример тестового пода находится в `./cuda-test-pod.yaml`. Примените его и проверьте логи:
    ```bash
    kubectl apply -f ./cuda-test-pod.yaml
    kubectl get pod cuda-test
    kubectl logs cuda-test
    ```
    В логах должен быть успешный вывод `nvidia-smi`.

