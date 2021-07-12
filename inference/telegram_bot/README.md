## Telegram bot

Используемая python-библиотека для взаимодействия с Telegram API

`https://pypi.org/project/python-telegram-bot/`

Для замены бота достаточно в `cfg.json` в значение поля `token` прописать токен вашего бота.

### Запуск

```
python image_sender.py
```

### Docker

Для сборки образа из директории `inference` выполнить команду:

```
DOCKER_BUILDKIT=1 docker build -t tgbot -f telegram_bot/Dockerfile .
```

Пример запуска образа:

```
docker run -d --rm --net host -v <host_shared_dir_for_photos>:/workspace/photos tgbot python image_sender.py
```
