# Инструкция по добавлению GPU-нод в кластер Deckhouse с NVIDIA GPU Operator

Этот документ описывает процесс добавления статических (bare metal) GPU-нод в кластер Deckhouse, используя NVIDIA GPU Operator для автоматического управления драйверами, контейнерным тулкитом и плагином устройств.

## Обзор процесса

1.  **Подготовка ноды:** Установка базовой ОС и подключение к кластеру Deckhouse.
2.  **Конфигурация Deckhouse:** Определение `NodeGroup` для GPU-нод.
3.  **Установка NVIDIA GPU Operator:** Развертывание оператора в кластере.
4.  **Настройка GPU Operator:** Конфигурация режимов работы GPU (Time-Slicing, Exclusive).
5.  **Валидация:** Проверка корректности установки и работы GPU.

## Детальный процесс

### Шаг 1: Подготовка ноды

1.  **Установите базовую операционную систему** (например, Ubuntu 22.04/24.04 LTS).
2.  **Подключите ноду к кластеру Deckhouse** с помощью bootstrap-скрипта, как описано в общей документации Deckhouse для статических нод. Убедитесь, что нода появилась в `kubectl get nodes`.

    **Получение Bootstrap-скрипта:**
    После применения `NodeGroup` Deckhouse автоматически создает секрет, содержащий одноразовый bootstrap-скрипт для этой группы.

    -   **Определите имя секрета.** Оно формируется по шаблону `manual-bootstrap-for-<имя-группы>`. Например, для `gpu-small` это будет `manual-bootstrap-for-gpu-small`.
    -   **Извлеките и сохраните скрипт.** Выполните команду, подставив нужное имя группы:
        ```bash
        # Для группы gpu-small
        kubectl -n d8-cloud-instance-manager get secret manual-bootstrap-for-gpu-small -o jsonpath='{.data.bootstrap\.sh}' | base64 -d > bootstrap-gpu-small.sh
        # Сделайте скрипт исполняемым
        chmod +x bootstrap-gpu-small.sh
        ```
        У вас появится исполняемый файл `bootstrap-gpu-small.sh`.

    -   **Скопируйте bootstrap-скрипт** на целевую ноду (замените `user` и `node-ip`):
        ```bash
        scp bootstrap-gpu-small.sh user@node-ip:~/ 
        ```
    -   **Зайдите на ноду** по SSH:
        ```bash
        ssh user@node-ip
        ```
    -   **Запустите скрипт** с правами `sudo`. Он выполнит все необходимые действия по установке и подключению к кластеру.
        ```bash
        sudo ./bootstrap-gpu-small.sh
        ```
    -   Через несколько минут нода должна появиться в выводе команды `kubectl get nodes`.

3.  **Убедитесь, что на ноде нет установленных драйверов NVIDIA** или других компонентов, которые могут конфликтовать с GPU Operator. Если ранее были установлены драйверы вручную или через `NodeGroupConfiguration`, выполните их полную очистку:

    **Примечание:** NVIDIA GPU Operator автоматически обрабатывает отключение драйвера `nouveau`. Однако, если после установки оператора GPU не обнаруживаются, возможно, потребуется ручное отключение `nouveau`:
    ```bash
    ssh user@node-ip "echo -e 'blacklist nouveau\noptions nouveau modeset=0' | sudo tee /etc/modprobe.d/blacklist-nouveau.conf"
    ssh user@node-ip "sudo update-initramfs -u"
    ssh user@node-ip "sudo reboot"
    ```
    -   **Удаление пакетов NVIDIA:**
        ```bash
        ssh user@node-ip "sudo apt-get purge -y nvidia-driver-* nvidia-container-toolkit*"
        ```
    -   **Удаление репозитория NVIDIA:**
        ```bash
        ssh user@node-ip "sudo rm -f /etc/apt/sources.list.d/nvidia-container-toolkit.list"
        ```
    -   **Очистка `apt`:**
        ```bash
        ssh user@node-ip "sudo apt-get autoremove -y && sudo apt-get clean"
        ```
    -   **Перезагрузка ноды:**
        ```bash
        ssh user@node-ip "sudo reboot"
        ```
    -   **Проверка чистоты:** После перезагрузки убедитесь, что `nvidia-smi` не работает (`command not found`).

### Шаг 2: Конфигурация Deckhouse NodeGroup

1.  **Определите `NodeGroup`** для ваших GPU-нод. Пример конфигурации находится в файле `infra/gpu_nodes/gpu-nodegroups.yaml`.
    -   **`gpu-small`:** Для GPU с меньшим объемом памяти, использующих `Time-Slicing`.
    -   **`gpu-standard`:** Для GPU с большим объемом памяти, использующих `Exclusive` доступ.

    **Важно:** В `nodeTemplate.labels` добавьте лейбл `nvidia.com/device-plugin.config` с именем конфигурации, которую вы определите в `values.yaml` GPU Operator (см. Шаг 4).
    Также добавьте `taint` `nvidia.com/gpu:NoSchedule`, чтобы предотвратить запуск подов без запроса GPU на этих нодах.

2.  **Примените конфигурацию `NodeGroup`:**
    ```bash
    kubectl apply -f infra/gpu_nodes/gpu-nodegroups.yaml
    ```

### Шаг 3: Установка NVIDIA GPU Operator

NVIDIA GPU Operator автоматизирует установку и управление всеми компонентами NVIDIA (драйверы, контейнерный тулкит, `device-plugin`, NFD, DCGM Exporter).

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
        helm show values nvidia/gpu-operator > infra/gpu_nodes/gpu-operator/original-values.yaml
        ```
    -   Создайте кастомный `values.yaml` (пример: `infra/gpu_nodes/gpu-operator/values.yaml`), где вы определите конфигурации `devicePlugin` для `Time-Slicing` и `Exclusive` режимов.

4.  **Установите GPU Operator:**
    ```bash
    helm install gpu-operator nvidia/gpu-operator \
      --namespace gpu-operator \
      --create-namespace \
      -f infra/gpu_nodes/gpu-operator/values.yaml
    ```

### Шаг 4: Валидация

1.  **Проверьте поды оператора:**
    Убедитесь, что все поды в неймспейсе `gpu-operator` находятся в статусе `Running` или `Completed`:
    ```bash
    kubectl get pods -n gpu-operator -o wide
    ```
    Особое внимание уделите `nvidia-driver-daemonset-*`, `nvidia-container-toolkit-daemonset-*` и `nvidia-device-plugin-daemonset-*`.

2.  **Проверьте ресурсы GPU на ноде:**
    Убедитесь, что Kubernetes видит GPU-ресурсы на вашей ноде:
    ```bash
    kubectl describe node kube-gpu-small-1
    ```
    В секциях `Capacity` и `Allocatable` должен появиться ресурс `nvidia.com/gpu` с соответствующим количеством (например, `4` для `Time-Slicing`).

3.  **Запустите тестовый CUDA Job:**
    Пример тестового пода находится в `infra/gpu_nodes/gpu-operator/cuda-test-pod.yaml`. Примените его и проверьте логи:
    ```bash
    kubectl apply -f infra/gpu_nodes/gpu-operator/cuda-test-pod.yaml
    kubectl get pod cuda-test
    kubectl logs cuda-test
    ```
    В логах должен быть успешный вывод `nvidia-smi`.
