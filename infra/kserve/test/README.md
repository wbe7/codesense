# KServe Installation Test

Этот документ описывает, как протестировать установку KServe, развернув простую модель и отправив ей запрос.

## 1. Развертывание модели

Сначала необходимо создать неймспейс для теста и развернуть в нем `InferenceService`. Мы используем `google/flan-t5-small`, так как это очень легковесная модель, которая гарантированно не вызовет проблем с ресурсами.

```bash
# Создаем неймспейс
kubectl create namespace kserve-test --dry-run=client -o yaml | kubectl apply -f -

# Разворачиваем модель
# Манифест находится в файле inferenceservice.yaml
kubectl apply -f infra/kserve/test/inferenceservice.yaml -n kserve-test
```

После этого необходимо дождаться, пока под с моделью запустится. Проверить статус можно командой:
```bash
kubectl get inferenceservice t5-llm -n kserve-test -w
```
Ожидайте, пока в колонке `READY` не появится `True`.

## 2. Тестовый запрос

Когда сервис готов, можно отправить ему запрос. Для модели `flan-t5-small` нужно использовать OpenAI-совместимый эндпоинт `/v1/completions`. Тело запроса находится в файле `chat-input-v1-completion.json`.

Выполните следующую команду:

```bash
curl -v -H "Content-Type: application/json" \
"https://t5-llm-kserve-test.kserve.cloudnative.space:7443/openai/v1/completions" \
-d @infra/kserve/test/chat-input-v1-completion.json
```

## 3. Ожидаемый результат

Вы должны получить ответ `HTTP/2 200 OK` и JSON с сгенерированным текстом в поле `text`. Это подтверждает, что вся цепочка от Gateway до модели работает корректно.

```json
{
  "id": "...",
  "object": "text_completion",
  "choices": [{
    "index": 0,
    "text": "...",
    "logprobs": null,
    "finish_reason": "length"
  }],
  ...
}
```