# Вторая практическая работа. Вариант 14

Инструмент для анализа графа зависимостей пакетов Cargo. Программа читает параметры командной строки.
На втором этапе она
запрашивает файл пакета из HTTP-индекса Cargo и выводит прямые
зависимости, объявленные для указанной версии.

## Запуск

Требуется Python 3.10 или новее. На macOS и Linux используйте `./run.sh`.
На Windows используйте `py -3 -m src.main` с теми же опциями. Установка
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

## Данные из Cargo

Официальный sparse-индекс хранит отдельный файл для каждого пакета.
Каждая строка файла содержит JSON с версией, зависимостями и служебными
полями. Например, файл пакета `quote` имеет путь `qu/ot/quote`.
В выводе указаны имя, ограничение версии, тип, optional и цель платформы,
если она объявлена. Локальный JSON используется начиная с этапа 3.

```sh
./run.sh --package quote --version 1.0.40 --repository https://index.crates.io/
./run.sh --package quote --version 999.0.0
```

[Формат индекса Cargo](https://doc.rust-lang.org/cargo/reference/registry-index.html)
