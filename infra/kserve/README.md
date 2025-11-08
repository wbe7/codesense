# Установка KServe

В этом документе описан пошаговый процесс установки KServe с использованием Gateway API.

## 1. Установка базовых API (CRDs)

Первым шагом необходимо установить Custom Resource Definitions (CRDs), которые добавляют в Kubernetes новые типы ресурсов.

### 1.1. Gateway API CRDs

Эти CRD добавляют ресурсы `Gateway`, `GatewayClass`, `HTTPRoute` и другие, необходимые для работы новой сетевой модели в Kubernetes.

```bash
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/standard-install.yaml
```

### 1.2. KServe CRDs

Эти CRD добавляют основной ресурс `InferenceService`, а также связанные с ним `TrainedModel` и `InferenceGraph`. Мы устанавливаем их с помощью официального Helm-чарта. Эта команда также создаст неймспейс `kserve`.

```bash
helm install kserve-crd oci://ghcr.io/kserve/charts/kserve-crd --version v0.15.0 --namespace kserve --create-namespace
```

## 2. Развертывание сетевого контроллера

Теперь, когда в кластере есть определения для Gateway API, нужно установить сам контроллер, который будет их реализовывать. Мы используем Envoy Gateway — одну из эталонных реализаций Gateway API.

Устанавливаем его с помощью Helm в отдельный неймспейс `envoy-gateway-system`.

```bash
helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.5.4 -n envoy-gateway-system --create-namespace
```

## 3. Создание и настройка шлюза

На этом этапе мы создаем саму точку входа в кластер для KServe. Все конфигурации хранятся в виде YAML-файлов в этой же директории (`infra/kserve`).

### 3.1. Создание GatewayClass

`GatewayClass` — это шаблон для создания шлюзов. Мы создаем один класс для Envoy.

```bash
kubectl apply -f infra/kserve/01-gatewayclass.yaml
```

### 3.2. Создание Gateway

Создаем сам шлюз, указывая для него наш `GatewayClass`, статический IP-адрес и порты. Это действие приведет к созданию Service типа LoadBalancer.

```bash
kubectl apply -f infra/kserve/02-gateway.yaml
```

### 3.3. Выпуск сертификата

Создаем ресурс `Certificate`, который `cert-manager` использует для автоматического выпуска wildcard-сертификата и его привязки к нашему шлюзу.

```bash
kubectl apply -f infra/kserve/03-certificate.yaml
```

## 4. Установка KServe

Теперь, когда вся необходимая инфраструктура готова, устанавливаем сам KServe.

### 4.1. Конфигурация KServe

Мы управляем конфигурацией KServe через специальный `values.yaml` файл. В ходе отладки мы выяснили правильную, рабочую структуру этого файла.

**Важно:** Несмотря на то, что в документации KServe может упоминаться `deploymentMode: Standard`, на практике для Helm-чарта `v0.15.0` рабочим значением оказалось `RawDeployment`.

Содержимое файла `infra/kserve/values.yaml`:
```yaml
kserve:
  controller:
    # Указываем режим 'RawDeployment', который эквивалентен 'Standard'
    deploymentMode: RawDeployment
    gateway:
      # Наш базовый домен
      domain: "kserve.cloudnative.space"
      # Генерировать https-ссылки
      urlScheme: "https"
      # Шаблон для URL, который покрывается wildcard-сертификатом (*.kserve.cloudnative.space)
      domainTemplate: "{{ .Name }}.{{ .Namespace }}.{{ .IngressDomain }}"
      # Секция для указания нашего шлюза
      ingressGateway:
        enableGatewayApi: true
        kserveGateway: "kserve/kserve-ingress-gateway"
```

### 4.2. Установка Helm-чарта

Устанавливаем KServe (или обновляем, если он уже был установлен) с применением нашей конфигурации.

```bash
helm upgrade -i kserve oci://ghcr.io/kserve/charts/kserve --version v0.15.0 -n kserve -f infra/kserve/values.yaml
```

После обновления рекомендуется перезапустить контроллер, чтобы он гарантированно подхватил все изменения.
```bash
kubectl rollout restart deployment kserve-controller-manager -n kserve
```

## 5. Настройка S3 хранилища (Опционально)

Чтобы KServe мог скачивать модели из вашего приватного S3-совместимого хранилища, необходимо выполнить два шага.

### 5.1. Создание секрета

Сначала нужно создать Kubernetes-секрет с вашими учетными данными. KServe по умолчанию ищет секрет с именем `storage-config`. Выполните команду ниже, подставив ваши реальные ключи вместо `YOUR_ACCESS_KEY` и `YOUR_SECRET_KEY`.

```bash
kubectl create secret generic storage-config -n kserve \
  --from-literal=AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY' \
  --from-literal=AWS_SECRET_ACCESS_KEY='YOUR_SECRET_KEY'
```

### 5.2. Обновление конфигурации KServe

Добавьте в `infra/kserve/values.yaml` секцию `storage`, чтобы указать эндпоинт вашего S3.

```yaml
# infra/kserve/values.yaml

kserve:
  # ... (секция controller) ...

  storage:
    s3:
      endpoint: "http://192.168.77.7:9000"
      useHttps: "0"
      verifySSL: "0"
      region: "" # Оставляем пустым, если не используется
```

После этого примените изменения командой `helm upgrade`, как в шаге 4.2.

## 6. Тестирование

После установки необходимо провести тестирование, развернув тестовую модель. Подробная инструкция находится в `infra/kserve/test/README.md`.
