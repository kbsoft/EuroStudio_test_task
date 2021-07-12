# EuroStudio_test_task
Тестовое задание (работа с данными)

Данная работа выполнена в рамках реализации тестового задания. 

Целью данного проверочного задания является определение уровня компетенций претендента в области машинного обучения и работы с соответствующим стеком технологий (нейронные сети, фреймворки, модели).

В рамках настоящего задания было проведено обучение ML-модели (нейронных сети) на задаче распознавания изображений с предоставлением результата в виде REST API сервиса и Telegram-бота.

## Результаты
### Набор данных
* [Ссылка](https://disk.yandex.ru/d/JW8zDLTU6_w89A) на архив с тестовым набором изображений (mod_dataset_test.zip).
* [Ссылка](https://disk.yandex.ru/d/q5BVePjt_qQ_7A) на архив с обучающим набором изображений (mod_dataset_train.zip).
* [Ссылка](https://disk.yandex.ru/d/dB6b7tChtM3SRw) хранилище с примерами изображений тестового набора.

### Демонстрация работы через Telegram-бот
Для проверки результатов работы обученной ML-модели (нейронных сети) можно воспользоваться Telegram-ботом и для этого рекомендуется выполнить следующие шаги:
1. Скачать по [ссылке](https://disk.yandex.ru/d/JW8zDLTU6_w89A) и разархивировать тестовый набор изображений или скачать несколько изображений из примеров по следующей [ссылке](https://disk.yandex.ru/d/dB6b7tChtM3SRw).
2. В Telegram-клиенте найти по имени бот @ClsEffnetTZUploaderBot и перейти в чат с ним.
3. Нажать кнопку "START", если чат с ботом ещё не доступен.
4. Загрузить любым возможным способом (*предпочтительней загружать изображение без сжатия - как документ*) произвольное изображение из тестового набора изображений и дождаться пока бот пришлет результат. 
5. Повторить п. 4 произвольное количество раз.

В качестве результата классификации изображения бот должен вернуть:
* идентификатор класса;
* название классифицированного объекта;
* степень уверенности ML-модели (нейронных сети) в том что изображение относится к данному классу.

**Замечание.** Если загрузить произвольное изображение не из тестового набора, то ML-модель (нейронная сеть) отнесет его к одному из классов из обучающего набора, но как правило степень уверенности нейронной сети будет ниже чем для примеров из целевого домена. 

### Демонстрация работы через Веб
Демонстрация работы ML-модели (нейронных сети) может быть выполнена через Веб в окне браузера и для этого рекомендуется выполнить следующие шаги:
1. Скачать по [ссылке](https://disk.yandex.ru/d/JW8zDLTU6_w89A) и разархивировать тестовый набор изображений или скачать несколько изображений из примеров по следующей [ссылке](https://disk.yandex.ru/d/dB6b7tChtM3SRw).
2. Открыть в окне Веб-браузера адрес [http://138.91.57.227/](http://138.91.57.227).
3. На открывшейся странице нажать кнопку "Обзор" (или "Browse"), выберать произвольное изображение из тестового набора изображений, а затем нажать кнопку "Загрузить" (или "Upload") и дождаться результата. 
4. Повторить п. 3 произвольное количество раз.

### Информация об ML-модели (нейронной сети)
* **Используемая архитектура:** EfficientNet;
* **Код подготовки (в т.ч. разбиения)  датасета (в формате Jupyter Notebook):** [dataset_prep.ipynb](https://github.com/kbsoft/EuroStudio_test_task/blob/main/dataset_prep.ipynb);
* **Код программы для обучения модели (в формате Jupyter Notebook):** [training.ipynb](https://github.com/kbsoft/EuroStudio_test_task/blob/main/training.ipynb);
* **Визуализация графиков обучающих метрик (с помощью сервиса neptune.ai):** [логи обучения](https://app.neptune.ai/mrtahion/mod-cls-effnet/e/MOD-14/charts);
* **Визуализация метаинформации (с помощью сервиса neptune.ai):** [metadata](https://app.neptune.ai/mrtahion/mod-cls-effnet/e/MOD-14/all);
* **Код программы для инференса:** [run_cls.py](https://github.com/kbsoft/EuroStudio_test_task/blob/main/inference/cls_effnet/classifier/run_cls.py).
