"""
Класс для взаимодействия с RabbitMQ сервером, основанный на библиотеке pika.
"""
import logging
from abc import ABCMeta, abstractmethod

import pika
from retry.api import retry_call


class AbstractRMQManager(metaclass=ABCMeta):
    def __init__(
        self,
        user,
        password,
        host,
        port=5672,
        delay=5,
        tries=5,
    ):
        """
        Инициализация подключения к RabbitMQ серверу.

        :param user: имя пользователя для авторизации
        :param password: пароль пользователя
        :param host: ip-адрес RabbitMQ сервера
        :param port: порт RabbitMQ сервера; default - 5672
        :param delay: время задержки между попытками соединения с сервером; default - 5
        :param tries: количество попыток соединения с сервером; default - 5
        """
        # TODO: initalize parameters in abstract class
        pass

    @abstractmethod
    def queue_declare(self, queue_name):
        """
        Определение очереди.

        :param queue_name: имя очереди
        """
        raise NotImplementedError

    @abstractmethod
    def exchange_declare(self, exchange_name, exchange_type):
        """
        Определение точки обмена.

        :param exchange_name: Имя точки обмена.
        :param echange_type: Тип точки обмена.
        Возможные значения: direct, fanout, topic, headers.
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, routing_key, message):
        """
        Отправляет сообщениe по указанному ключу маршрута

        :param routing_key: Для очереди - название очереди.
        Для точки обмена - ключ маршрута, по которому подписчики определят
        для кого пришлосообщение.
        Для точки обмена типа fanout - пустая строка.
        :param message: Текст сообщения.
        """
        raise NotImplementedError

    @abstractmethod
    def listen(self, routing_key, callback):
        """
        Стартует прослушивание очереди или точки обмена с переданными настройками

        :param routing_key: Для очереди - название очереди.
        Для точки обмена - ключ маршрута, по которому подписчик слушает паблишера.
        Собирает сообщения только от заданного ключа маршрута.
        Для точки обмена типа fanout - пустая строка.
        :param callback: Функция для обработки входящих сообщений.
        """
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class RMQManager(AbstractRMQManager):
    QUEUE = 0
    EXCHANGE = 1

    def __init__(
        self,
        user,
        password,
        host,
        port=5672,
        delay=5,
        tries=5,
    ):
        self.__delay = delay
        self.__tries = tries

        self.__user = user
        self.__pwd = password
        self.__host = host
        self.__port = port

        self.__conn_type = None
        self.__queue_name = None
        self.__exchange_name = None
        self.__exchange_type = None

        self.__start()

    def __start(self):
        retry_call(self.__create_connection, tries=self.__tries, delay=self.__delay)

    def __create_connection(self):
        logging.info(f"Connecting to {self.__host}:{self.__port} as {self.__user}...")
        self.__connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.__host,
                port=self.__port,
                heartbeat=10,
                credentials=pika.PlainCredentials(self.__user, self.__pwd),
            )
        )
        self.__channel = self.__connection.channel()

    def __reconnect(self):
        self.__start()

        if self.__conn_type == self.EXCHANGE:
            self.exchange_declare(self.__exchange_name, self.__exchange_type)
        elif self.__conn_type == self.QUEUE:
            self.queue_declare(self.__queue_name)

    def queue_declare(self, queue_name):
        self.__conn_type = self.QUEUE
        self.__exchange_name = ""
        self.__queue_name = queue_name
        self.__channel.queue_declare(queue=self.__queue_name)

    def exchange_declare(self, exchange_name, exchange_type):
        self.__conn_type = self.EXCHANGE
        self.__queue_name = ""
        self.__exchange_name = exchange_name
        self.__exchange_type = exchange_type
        self.__channel.exchange_declare(
            exchange=exchange_name, exchange_type=exchange_type
        )

    def send(self, routing_key, message):
        try:
            self.__channel.basic_publish(
                exchange=self.__exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(expiration="1000")
            )
        except (
            pika.exceptions.ConnectionClosedByBroker,
            pika.exceptions.StreamLostError,
        ):
            logging.error(
                f"Connection closed by peer on sending to '{routing_key}'."
                "Trying to reconnect..."
            )
            self.__reconnect()
            self.send(routing_key, message)

    def listen(self, routing_key, callback):
        if self.__conn_type == self.EXCHANGE:
            self.__channel.queue_declare(self.__queue_name, exclusive=True)
            self.__channel.queue_bind(
                exchange=self.__exchange_name,
                queue=self.__queue_name,
                routing_key=routing_key,
            )

        self.__channel.basic_consume(
            queue=self.__queue_name,
            on_message_callback=callback,
        )

        try:
            logging.info(f"Start to consuming {routing_key}")
            self.__channel.start_consuming()
        except KeyboardInterrupt:
            logging.error("Closing connection by user...")
            self.__channel.stop_consuming()
            self.__connection.close()
            logging.error("Connection closed by user.")
        except pika.exceptions.ConnectionClosedByBroker:
            logging.error(
                f"Connection closed by peer on consuming '{routing_key}'."
                "Trying to reconnect..."
            )
            self.__reconnect()
            self.listen(routing_key, callback)

    def close(self):
        self.__connection.close()


class DummyRMQManager(AbstractRMQManager):
    """Implementation of AbstractRMQManager which does nothing.
    Useful for debugging and testing purposes
    """

    def __init__(
        self,
        user,
        password,
        host,
        port=5672,
        delay=5,
        tries=5,
    ):
        super().__init__(
            user,
            password,
            host,
            port=5672,
            delay=5,
            tries=5,
        )

    def queue_declare(self, queue_name):
        pass

    def exchange_declare(self, exchange_name, exchange_type):
        pass

    def send(self, routing_key, message):
        pass

    def listen(self, routing_key, callback):
        pass

    def close(self):
        pass
