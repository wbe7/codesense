# Установка и управление deployKF

Этот документ описывает процесс установки и управления deployKF с использованием подхода GitOps и ArgoCD.

## Предварительные требования

Перед началом убедитесь, что у вас установлены следующие инструменты:

- `deploykf` CLI
- `kubectl`
- `argocd` CLI
- `bash` версии 4.4+ (на macOS можно установить с помощью `brew install bash`)

## Установка

Процесс установки состоит из трех основных шагов:

### 1. Генерация манифестов

Манифесты Kubernetes для всех компонентов deployKF генерируются на основе файла `values.yaml`.

Для повторной генерации манифестов после внесения изменений в `values.yaml`, выполните следующую команду из корня репозитория:

```bash
deploykf generate --source-version 0.1.5 --values infra/deploykf/values.yaml --output-dir infra/deploykf/manifests
```

### 2. Установка ArgoCD

Мы используем специальный скрипт для установки ArgoCD с плагином deployKF.

Для установки ArgoCD выполните следующий скрипт из директории `infra/deploykf`:

```bash
bash ./install_argocd.sh
```

Это установит ArgoCD в namespace `argocd` и настроит его с необходимыми компонентами.

### 3. Развертывание "App of Apps"

После установки ArgoCD необходимо развернуть главное приложение "App of Apps", которое указывает ArgoCD, где найти манифесты для всех остальных приложений.

Примените манифест `app-of-apps.yaml`:

```bash
kubectl apply -f infra/deploykf/manifests/app-of-apps.yaml
```

## Синхронизация

После создания "App of Apps" вы можете синхронизировать все приложения deployKF с помощью предоставленного скрипта.

Скрипт запросит у вас режим очистки (prune mode) в интерактивном режиме. Рекомендуется использовать `ALWAYS prune`.

Для запуска скрипта синхронизации выполните следующую команду из директории `infra/deploykf`:

```bash
bash ./sync_argocd_apps.sh
```

**Примечание:** Убедитесь, что в вашей системе `bash` указывает на исполняемый файл версии 4.4+.

## Конфигурация

- **Основная конфигурация**: Основная конфигурация стека deployKF управляется в файле `values.yaml`.
- **Cert-Manager**: Если вы используете Deckhouse, модуль `cert-manager` настраивается через отдельный файл `cert-manager-config.yaml`, который необходимо применять к кластеру вручную.

## Устранение неисправностей

### Ошибка admission webhook при создании подов

Если вы используете Deckhouse, его политики безопасности могут блокировать создание подов в некоторых неймспейсах. В этом случае необходимо вручную добавить лейбл к неймспейсу, чтобы разрешить запуск привилегированных подов.

Выполните следующие команды для соответствующих неймспейсов:

#### `deploykf-auth`
```bash
kubectl label namespace deploykf-auth security.deckhouse.io/pod-policy=privileged
```

#### `deploykf-dashboard`
```bash
kubectl label namespace deploykf-dashboard security.deckhouse.io/pod-policy=privileged
```
