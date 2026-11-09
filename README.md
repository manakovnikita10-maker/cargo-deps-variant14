# Вторая практическая работа. Вариант 14

Инструмент для анализа графа зависимостей пакетов Cargo. На первом этапе
программа читает параметры и выводит их в формате «ключ = значение».

## Запуск

Требуется Python 3.10 или новее. На macOS и Linux используйте `./run.sh`.
На Windows используйте `py -3 src/main.py` с теми же опциями. Установка
Python-библиотек и сборка не нужны.

| Параметр | Назначение |
| --- | --- |
| `--package` | Имя пакета. В тестовом режиме используется буква A–Z. |
| `--version` | Полная версия пакета Cargo. Обязательна в сетевом режиме. |
| `--repository` | URL индекса Cargo или путь к локальному JSON. По умолчанию используется индекс crates.io. |
| `--test` | Читать тестовый репозиторий из файла. |
| `--filter` | Подстрока имени для исключения пакетов. |

```sh
./run.sh --package quote --version 1.0.40 --filter ident
./run.sh --test --repository tests/graph.json --package A
python3 -m unittest discover -s tests -v
```

Команды с ошибочными значениями возвращают код 2 и сообщение о параметре.
Примеры для защиты этапа:

```sh
./run.sh --package ../quote --version 1.0.40
./run.sh --package quote --version 1.0
./run.sh --package quote --version 1.0.40 --repository invalid
./run.sh --test --package A
./run.sh --package quote --version 1.0.40 --filter " "
```
