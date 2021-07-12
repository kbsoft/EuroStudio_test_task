# RMQ

Модуль для взаимодействия с RabbitMQ очередями и точками обмена.

Опциональные параметры:
    
    - 'port' - порт RabbitMQ-сервера; default 5672

    - 'delay' - задержка в секундах между попытками подключения к серверу; default 5

    - 'tries' - количество попыток подключения к серверу; default 5

### Примеры использования мэнеджера


```python
# Установка соединения с сервером
rmq = RMQManager(user, password, host)

# Определение очереди
rmq.queue_declare("routing_key")

# Определение точки обмена
rmq.exchange_declare("exchange_name", "direct")

# Отправка сообщения
# Если объявлена точка обмена типа fanout, то routing_key = ""
rmq.send("routing_key", "message")

# Пример колбэка для подписчика
def callback(ch, method, properties, body):
    # Содержимое сообщения хранится в `body`
    data = json.loads(body)
    print(data)

# Получение сообщений подписчиком.
# Если объявлена точка обмена типа fanout, то routing_key = ""
thread = Thread(
    target=rmq.listen,          # За получение сообщений отвечает метод мэнеджера listen.
    args=("routing_key", callback,),    # За обработку сообщений метод callback, передаваемый в параметрах.
    daemon=True,
)
thread.start()
```
