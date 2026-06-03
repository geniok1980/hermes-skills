---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault via Яндекс.Диск WebDAV.
platforms: [linux]
---

# Obsidian Vault (Евгений)

## Use Rules

**Триггер:** Когда пользователь говорит «создай md файл», «создай заметку», «напиши навык», «сохрани информацию», «запиши в заметки» → всегда создавать файл в Obsidian vault через WebDAV на Яндекс.Диск, а не локально.

**Исключение:** Если пользователь явно указал другой путь или просто просит «запиши в файл» без уточнения «заметка»/«md» — создавать локально, если не указано иное.

**Путь по умолчанию:** `https://webdav.yandex.ru/Obsidian%20Vault/Папка/Название.md`

## Подключение

Vault синхронизируется через **Remotely Save** плагин → **WebDAV** → **Яндекс.Диск**.

- **WebDAV сервер:** `https://webdav.yandex.ru`
- **Vault path на диске:** `/Obsidian%20Vault/` (он же `https://webdav.yandex.ru/Obsidian%20Vault/`)
- **Логин:** `geniok1980@yandex.ru`
- **Пароль приложения:** `aliuiwknyyekrdfg`

> Credentials сохранены в памяти Hermes — доступны при загрузке навыка.

## Основные операции (curl с базовой аутентификацией)

Для всех запросов используй:
```
AUTH="-u geniok1980@yandex.ru:aliuiwknyyekrdfg"
BASE="https://webdav.yandex.ru/Obsidian%20Vault"
```

### 📋 Список заметок
```bash
curl -s $AUTH -X PROPFIND -H "Depth: 1" "$BASE/" | grep -oP '<d:href>[^<]+</d:href>' | sed 's/<[^>]*>//g'
```

### 📖 Чтение заметки
```bash
curl -s $AUTH "$BASE/Hermes%20Agent.md"
```

### ✏️ Создание/обновление заметки
```bash
# Вариант 1: загрузить локальный файл (рекомендуется для больших файлов)
curl -s $AUTH -T "/tmp/note.md" "$BASE/Folder/Note.md"

# Вариант 2: PUT с телом из stdin
echo "# Заголовок" | curl -s $AUTH -X PUT --data-binary @- "$BASE/Folder/Note.md"
```

> ⚠️ **Питфолл:** Для больших файлов (10+ КБ) используй **Вариант 1** (`-T /tmp/file`). 
> Сначала запиши содержимое в локальный файл (через write_file), затем загружай.
> Вариант 2 с heredoc внутри execute_code может выполняться **>2 мин** из-за передачи 
> большого объёма данных через Python subprocess.

### 📂 Создание папки
```bash
curl -s $AUTH -X MKCOL "$BASE/New%20Folder/"
```

### 🔍 Поиск (PROPFIND с Depth: infinity)
```bash
curl -s $AUTH -X PROPFIND -H "Depth: infinity" "$BASE/" | python3 -c "
import sys, xml.etree.ElementTree as ET, urllib.parse
data = sys.stdin.read()
root = ET.fromstring(data)
ns = {'d': 'DAV:'}
for resp in root.findall('.//d:response', ns):
    href = resp.find('d:href', ns).text
    name = urllib.parse.unquote(href.split('/')[-1])
    print(name)
"
```

### 🗑️ Удаление заметки
```bash
curl -s $AUTH -X DELETE "$BASE/Obsolete%20Note.md"
```

## Структура vault

```
/Obsidian Vault/
├── Hermes Agent.md        — центр (главная заметка)
├── Skills/                — навыки
├── Projects/              — проекты
├── geniok/
├── Проекты/
└── Юпитер/
```

## Wikilinks

Obsidian линкует заметки через `[[Note Name]]`. При создании заметок используй их для связывания.

### 📦 Bulk upload с подпапками (много файлов, организация как в источнике)

Для загрузки целой папки с вложенными подпапками (результат краула документации):

**⚠️ Критическое правило:** Перед загрузкой файлов ВСЕГДА создавай (`MKCOL`) целевые директории на WebDAV. Yandex.WebDAV НЕ создаёт их автоматически. Файлы, загруженные в несуществующую папку, возвращают `curl: (25) Failed to upload`.

**Шаги:**

1. Собрать все .md файлы с их относительными путями
2. Создать все уникальные подпапки на WebDAV через `MKCOL`
3. Загрузить файлы параллельными батчами (BATCH_SIZE=10)
4. Проверить: у загруженных файлов должен отсутствовать `<d:collection/>` в `resourcetype`

```python
import asyncio, os

BATCH_SIZE = 10  # оптимально для Yandex WebDAV

async def ensure_dir(webdav_base, path, auth):
    """Создать директорию на WebDAV (если не существует)."""
    url = f"{webdav_base}/{path}"
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", auth, "-X", "MKCOL", url,
        "-w", "%{http_code}", "-o", "/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await proc.communicate()
    return out.decode().strip() in ('201', '200', '204')

async def upload_one(local_path, remote_path, webdav_base, auth) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", auth, "-T", local_path,
        f"{webdav_base}/{remote_path}",
        "-w", "%{http_code}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await proc.communicate()
    return out.decode().strip() in ('201', '204', '200')

async def bulk_upload(source_dir, webdav_base, auth):
    # 1. Собрать все .md файлы
    files = []
    dirs = set()
    for root, _, fnames in os.walk(source_dir):
        for f in fnames:
            if not f.endswith('.md'): continue
            rel_dir = os.path.relpath(root, source_dir)
            remote = f if rel_dir == '.' else f"{rel_dir}/{f}"
            files.append((os.path.join(root, f), remote))
            if rel_dir != '.':
                dirs.add(rel_dir)
    
    # 2. Создать подпапки
    for d in sorted(dirs):
        await ensure_dir(webdav_base, d, auth)
    
    # 3. Загрузить батчами
    uploaded = 0
    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i:i+BATCH_SIZE]
        results = await asyncio.gather(*[
            upload_one(local, remote, webdav_base, auth)
            for local, remote in batch
        ])
        uploaded += sum(1 for r in results if r)
        if (i + BATCH_SIZE) % 100 == 0 or (i + BATCH_SIZE) >= len(files):
            print(f"  [{uploaded}/{len(files)}] uploaded")

# Пример использования:
# source = "/root/rkeeper-full-docs/docs"
# base = "https://webdav.yandex.ru/Obsidian%20Vault/rkeeper-docs/full"
# auth = "user:pass"
# asyncio.run(bulk_upload(source, base, auth))
```

> ⚠️ **Питфолл:** Если после загрузки PROPFIND показывает файлы с `resourcetype: <d:collection/>` — они загрузились как директории, а не как файлы. Причина: родительская папка не существовала к моменту загрузки.
>
> **Проверка через PROPFIND:**
> ```bash
> curl -s -u "user:pass" -X PROPFIND -H "Depth: 1" "$BASE/path/" | grep -A1 '<d:href>.*\.md</d:href>'
> # Если видете <d:collection/> — файл стал директорией, надо перезалить
> ```
>
> **Быстрая проверка успешности загрузки (по всем подпапкам):**
> ```bash
> # Проверить количество файлов (getcontentlength) в каждой подпапке
> for d in subdir1 subdir2; do
>   count=$(curl -s -u "user:pass" -X PROPFIND -H "Depth: 1" "$BASE/$d/" | grep -c 'getcontentlength')
>   echo "$d: $count files"
> done
> ```
> Если везде `0 files` — родительские папки не были созданы. Удали всё через `DELETE`, создай папки через `MKCOL`, повтори загрузку.
>
> **Сценарий «0 загруженных из N»:** Если после удаления родительской папки (`DELETE`) и повторного запуска скрипт показывает `0/N uploaded` — значит `WEBDAV_BASE` (папка назначения) не существует. Сначала создай её и все подпапки через `MKCOL`, затем запускай загрузку. <br>
> ✅ **Правильный порядок:** `MKCOL root` → `MKCOL subdirs` → `curl -T files`

### 📝 Создание index-заметки со ссылками на все файлы

```python
idx = ["# My Project Docs", "", "## Содержание", ""]
for fname in sorted(os.listdir("/local/path/docs")):
    if fname.endswith('.md'):
        idx.append(f"- [[docs/{fname.replace('.md', '')}|{fname.replace('.md', '').replace('-', ' ').title()}]]")

with open("/tmp/index.md", 'w') as f:
    f.write('\n'.join(idx))
# Загрузить index
await webdav_upload("/tmp/index.md", "MyProject/index.md")
```

## Architecture полной связки

```
┌─ Сервер (Hermes) ─────────────────────┐
│  curl + WebDAV ─→ Яндекс.Диск         │
│       ↕ Remotely Save                 │
│  Obsidian (Docker, порт 3000)         │
└────────────────────────────────────────┘
             ↕ WebDAV
┌─ Windows ──────────────────────────────┐
│  Obsidian → Remotely Save → WebDAV     │
└────────────────────────────────────────┘
```

## Документация сайтов → Obsidian (Crawl4AI)

Для импорта целых документационных сайтов (Confluence, ReadTheDocs и т.д.) используй навыки:

1. **`crawl4ai`** — установка и настройка Crawl4AI, паттерны обхода, извлечение контента
2. **`web-scraping`** — полный пайплайн: discovery → crawl → save → upload

**Типовой сценарий:**
```python
# 1. Установить crawl4ai
source /root/crawl4ai-env/bin/activate
pip install -U crawl4ai && crawl4ai-setup

# 2. Создать скрипт в /root/.hermes/scripts/ (с shebang на venv)
#!/root/crawl4ai-env/bin/python3

# 3. Загружать через curl -T (НЕ heredoc)
async def webdav_upload(local, remote):
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", "user:pass", "-T", local,
        f"https://webdav.yandex.ru/Obsidian%20Vault/Folder/{remote}",
        "-w", "%{http_code}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await proc.communicate()
    return out.decode().strip() in ('201', '204', '200')
```

## Синхронизация

- При изменении заметок через WebDAV, Remotely Save на Windows подхватит изменения автоматически (или по триггеру).
- При создании заметок через curl — они сразу попадают на Яндекс.Диск и далее синхронизируются на все клиенты.

## Reusable scripts

- `scripts/bulk-upload-webdav.py` — параллельная загрузка всех `.md` из папки с подпапками на WebDAV. Использование:
  ```bash
  python3 /root/.hermes/skills/note-taking/obsidian/scripts/bulk-upload-webdav.py \
      /path/to/source \
      "https://webdav.yandex.ru/Obsidian%20Vault/remote/folder" \
      "login:password" \
      10
  ```
