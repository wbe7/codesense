# Code Intelligence Assistant (CIA)

Этот проект представляет собой Self-Hosted Code Intelligence Assistant (CIA) — AI-систему, которая отвечает на вопросы по внутренней кодовой базе, используя RAG и (опционально) fine-tuned small LLM.

## Начало работы

### 1. Настройка виртуального окружения

Для изоляции зависимостей проекта используется виртуальное окружение Python. Создайте и активируйте его следующими командами:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Установка зависимостей

Установите все необходимые пакеты, перечисленные в `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Настройка DVC

DVC используется для версионирования данных (кодовых баз). Вам необходимо настроить учетные данные для доступа к удаленному хранилищу S3. Создайте файл `.dvc/config.local` и добавьте в него свои учетные данные:

```bash
dvc remote modify --local s3-remote access_key_id YOUR_ACCESS_KEY_ID
dvc remote modify --local s3-remote secret_access_key YOUR_SECRET_ACCESS_KEY
```

Замените `YOUR_ACCESS_KEY_ID` и `YOUR_SECRET_ACCESS_KEY` вашими реальными ключами.

### 4. Загрузка данных

После настройки DVC загрузите кодовые базы, которые используются в качестве датасета:

```bash
dvc pull
```

## Управление кодовыми базами

Для получения дополнительной информации об управлении кодовыми базами см. `codebases/README.md`.
