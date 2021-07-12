## Требования

1. Docker v20.10+.
2. Docker-compose v1.28+.

### Управление

Загрузка через Телеграм бота

```
docker-compose -p bot --profile bot up -d
```

Загрузка через web-страницу

```
docker-compose -p web --profile web up -d
```

Просмотр логов

```
docker-compose logs -f
```

Остановка 
```
docker-compose stop
```
