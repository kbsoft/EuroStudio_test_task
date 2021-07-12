## API

Фреймворк - Flask.

### Запуск

Перейти в директорию `webapi` и выполнить ряд команд:

```
export FLASK_APP=api
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Docker

Для сборки образа перейти в директорию `webapi` и выполнить команду:

```
DOCKER_BUILDKIT=1 docker build -t api .
```

Пример запуска образа:

```
docker run -d --rm --net host -v <host_shared_dir_for_photos>:/workspace/photos api flask run --host=0.0.0.0 --port=5000
```
