# Image Organizer CLI

Организует фото по датам (EXIF/mtime) в подкаталоги YYYY/MM/DD, опционально находит дубликаты по хэшу.

## Установка
```bash
pip install -r requirements.txt
```

## Запуск
```bash
python main.py --src "C:/path/to/photos" --dst "C:/path/to/output" --dedupe
```

## Параметры
- `--src` — исходная папка
- `--dst` — папка вывода
- `--dedupe` — включить удаление дубликатов (копии не создаются повторно)
