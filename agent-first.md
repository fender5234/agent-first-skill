# Agent-First Project Guide

Руководство по организации проекта для разработки и поддержки **исключительно через AI-агентов**.

---

## Главный принцип

**Всё что агент читает часто — должно быть дёшево, точно, машиночитаемо.**
**Всё что агент читает редко — может быть в любой форме, главное актуально.**

Каждый токен на "ориентирование" — это токен не потраченный на задачу.

---

## Структура проекта

```
documentation/
├── project.yaml              ← entry point для агента (супер-индекс)
├── frontend.yaml             ← карта фронта (блоки)
├── backend.yaml              ← карта бэка (сервисы, API)
├── <layer>.yaml              ← другие слои проекта
├── validate.py               ← проверка целостности
└── adr/                      ← архитектурные решения (append-only)
    ├── 001-*.md
    └── 002-*.md

scripts/
├── validate.sh               ← все проверки одной командой
├── dev.sh                    ← локальный запуск
└── deploy.sh                 ← деплой

CLAUDE.md                     ← правила для агента (entry points, autonomy)
```

---

## 1. Манифест-файлы (YAML как источник правды)

### project.yaml — точка входа
```yaml
layers:
  frontend: documentation/frontend.yaml
  backend: documentation/backend.yaml

key_files:
  entrypoint: app/main.py
  config: app/config.py

key_services:
  auth: app/services/auth_service.py

env:
  required: [DATABASE_URL, JWT_SECRET_KEY]
  optional: [OPENAI_API_KEY]

tests:
  smoke: pytest tests/smoke/
  run_before_merge: [smoke]

observability:
  logs: /var/log/app.log
  health_check: https://project.com/health
```

### <layer>.yaml — карта блоков слоя

Полный формат блока с механизмами защиты от забывчивости:

```yaml
blocks:
  bots-list:
    code_path: src/features/bots
    entry: BotsList.tsx
    summary: "CRUD ботов, таблица, фильтры"
    depends_on: [auth, api-client]
    related_blocks: [channels-list]
    api_calls:
      - GET /api/bots
      - POST /api/bots
    adr: [004, 007]
    gotchas:
      - "Фильтрация клиентская — см. ADR-004"
      - "useMemo критичен для перфа"
    notes: |
      Клиентская фильтрация до 100 ботов.
      Серверная пагинация, лимит 50.
    last_modified_context: |
      2026-03: рефакторинг на новый endpoint /v2/bots
```

**Поля и их назначение:**

| Поле | Обязательное | Зачем |
|---|---|---|
| `code_path` | да | путь к папке блока (валидируется) |
| `entry` | да | главный файл (валидируется) |
| `summary` | да | 1 строка — что делает блок |
| `depends_on` | нет | явные зависимости от других блоков |
| `related_blocks` | нет | связанные блоки (проверить при изменениях) |
| `api_calls` | нет | список endpoints — актуальная карта API |
| `adr` | нет | номера ADR где обоснованы решения (валидируется) |
| `gotchas` | нет | подводные камни — агент читает ПЕРВЫМ делом |
| `notes` | нет | многострочный контекст "почему так" |
| `last_modified_context` | нет | короткая история последних изменений |

**Почему YAML, а не MD:**
- Структурированный поиск по ключу (O(1) вместо парсинга текста)
- Валидация по схеме
- Компактность для обзора (50 токенов vs 500)
- MD-описания переносятся в поле `notes: |` (multiline)

---

## 2. ADR (Architecture Decision Records)

Маленькие append-only файлы для фиксации "почему так".

**Формат (жёсткий):**
```markdown
# ADR 004: Client-side filtering
Status: accepted
Date: 2026-03-15
Affects: [bots-list, channels-list]

## Context
Проблема и контекст.

## Decision
Что решили.

## Consequences
+ Плюсы
- Минусы
```

**Правила:**
- Append-only (никогда не правим задним числом)
- Если решение устарело — создаём новое со статусом `supersedes 004`
- Ссылки на ADR указываются в поле `adr: [004]` блока YAML (массив номеров)
- В самом ADR указываются затронутые блоки в `Affects:` — даёт двустороннюю связь
- Заводим ADR **когда принимаем решение**, не ретроспективно

### Именование файлов
Формат: `documentation/adr/NNN-kebab-case-title.md`
- `001-multi-llm-factory.md`
- `002-keycloak-migration.md`
- `004-client-side-filtering.md`

Номер трёхзначный с ведущими нулями — упрощает сортировку и валидацию.

### Как агент работает с ADR

Агент читает ADR **не каждый раз**, а по триггеру:

| Задача | Читать ADR? |
|---|---|
| Простая правка (стиль, текст) | Нет |
| Задевает логику блока | Да, упомянутые в `adr:` |
| Рефакторинг блока | Обязательно все `adr:` блока |
| Работа с `gotchas` | Читать связанный ADR |

Это экономит токены — детальный контекст грузится только когда нужен.

### Двусторонняя валидация

Валидатор проверяет **обе стороны связи**:

1. **YAML → ADR:** если в блоке `adr: [004]` — файл `004-*.md` должен существовать
2. **ADR → YAML:** если ADR заявляет `Affects: [bots-list]` — в блоке `bots-list` должен быть `adr: [004]`

Рассинхронить невозможно — pre-commit заблокирует коммит.

---

## 3. CLAUDE.md — правила для агента

### Обязательные секции

**Agent entry points:**
```markdown
## Agent entry points
ALWAYS start here:
1. Read documentation/project.yaml to get the map
2. Read relevant layer YAML based on task
3. Only then open source code
```

**Task routing — выбор workflow по типу задачи:**
```markdown
## Task routing — choose workflow by task type

### New feature / new module → Full 9-step workflow
1. Orient — read project.yaml, find affected blocks
2. Read block context — output gotchas to user (mandatory)
3. ADR decision — apply 3-criteria rule
4. Write tests — key scenarios per module, BEFORE implementation
5. Implement — with context7, sequential-thinking, KISS/DRY/SOLID/Feature-Based
6. Run tests — green → continue, red → fix
7. Update YAML — manifests of affected blocks
8. Self-Check — verify code against all cross-cutting rules before commit
9. Commit — pre-commit validates

### Bug fix (logic/behavior) → Full 9-step workflow
Same steps. ADR likely "not needed", but tests mandatory to prevent regression.

### Bug fix (trivial: typo, text, style) → Light workflow
1. Orient — find affected block
2. Read gotchas
3. Fix
4. Commit

### Refactoring → Full 9-step workflow
Tests critical — prove behavior preserved. YAML update mandatory.

This applies to ALL tasks automatically, not only when user says "AF".
```

**Autonomy rules:**
```markdown
## Agent autonomy rules

### Do without asking:
- Читать код
- Запускать validate.sh
- Обновлять YAML после рефакторинга

### Ask before:
- Удалять файлы
- Менять схему БД
- Трогать .env / config
- Деплоить в прод

### Never do:
- push --force
- Коммитить secrets
- Менять ADR задним числом
```

---

## 4. Валидация (validate.py)

Скрипт проверяет целостность:

**Базовые проверки:**
- все `code_path` из манифестов существуют
- все `entry` файлы существуют
- нет "сирот" (папок без записи в манифесте)
- нет блоков в манифесте с битыми путями

**Проверки ссылочной целостности:**
- все номера ADR из `adr: [004]` ссылаются на существующие файлы
- все блоки из `Affects:` в ADR существуют в манифестах
- двусторонняя связь ADR ↔ блоки не нарушена
- все `depends_on` и `related_blocks` ссылаются на существующие блоки

Запускается:
- вручную после рефакторинга
- через pre-commit hook (локально)
- через CI на каждый PR

---

## 5. Уровни автоматизации синхронизации

Добавляй по мере боли, не сразу:

| Уровень | Что | Когда добавлять |
|---|---|---|
| **0** | Только дисциплина | Прототип |
| **1** | validate.py (ручной) | Всегда как минимум |
| **2** | pre-commit hook | Сразу после Уровня 1 |
| **3** | CI check | Появился второй разработчик ИЛИ обходишь pre-commit |
| **4** | Автогенерация манифеста из кода | 20+ блоков ИЛИ рефакторинг раз в неделю |
| **5** | Двусторонняя синхронизация с диаграммой | Почти никогда (overkill) |

**Pre-commit через framework** (`.pre-commit-config.yaml` в репо) — переносится между машинами. Голый `.git/hooks/` — нет.

---

## 6. Диаграммы

**Не храни вручную как источник правды.**

Варианты:
- **On-demand:** проси агента сгенерить mermaid из YAML когда нужно
- **Auto-generated:** скрипт YAML → mermaid/drawio, артефакт в репо но не редактируется вручную
- **Wallpaper:** если очень хочется красивую `.drawio` — веди вручную, но признай что это обложка, а не данные

---

## 7. Тесты как документация

В agent-first проекте тесты **критичнее** MD-документации:
- Агент может сломать неочевидное при рефакторинге
- Ревью реже → тесты = главный safety net
- Тесты точнее любого MD показывают "как должно работать"

Минимум:
- Smoke-тесты на критичные endpoints
- Интеграционные тесты для ключевых флоу
- 1-2 E2E сценария

Регистрируй в `project.yaml → tests` чтобы агент знал что запускать.

---

## 8. Скрипты вместо длинных инструкций

Одна команда = одно действие:
```bash
scripts/
├── dev.sh          # поднять локально
├── validate.sh     # все проверки
├── deploy.sh       # деплой
└── reset_dev.sh    # откатить окружение
```

Агент дёргает скрипт, не собирает bash-магию на лету.

---

## 9. Сквозные правила качества

Три правила, которые действуют **на каждом этапе** работы агента — ориентирование, ADR, реализация, ревью, drift audit.

### 9.1. Всегда использовать context7 для документации

Перед чтением, написанием или ревью кода — проверять актуальную документацию через context7. Касается: фреймворков, библиотек, стандартной библиотеки языка, инструментов сборки и тестирования.

**Никогда не полагаться на training data.** API меняется между версиями, best practices эволюционируют, deprecated паттерны сохраняются в training data.

**Баланс токенов:** экономия на навигации (YAML-карта вместо grep всего проекта) компенсирует расход на context7. Итоговый бюджет токенов примерно тот же, но качество кода выше.

### 9.2. Всегда использовать sequential-thinking для рассуждений

Перед любым нетривиальным решением — использовать sequential-thinking. Касается: ADR-решений, выбора подхода к реализации, оценки trade-offs, отладки сложных проблем, стратегии рефакторинга.

**Структура:** проблема → варианты → trade-offs → решение. Не "выстреливать первой мыслью".

### 9.3. Всегда применять KISS / DRY / SOLID при написании кода

Применяются **в процессе** написания, а не как отдельный шаг ревью:

**KISS:**
- Функция > 40 строк → разбить
- Вложенность > 3 уровней → рефакторить
- Если код требует комментария "почему" — возможно, решение слишком сложное

**DRY:**
- Перед написанием нового кода — grep проект на похожую логику
- Если 70%+ совпадение — переиспользовать, не дублировать
- 3 повторения — порог для абстракции (не раньше)

**SOLID (адаптированный):**
- S — один модуль/класс = одна ответственность
- O — новая функциональность через расширение, не модификацию существующего кода
- D — зависимости через абстракции, не через конкретные реализации

### 9.4. Test-First на уровне модуля

Перед реализацией модуля/фичи — написать тесты ключевых сценариев. Не на каждую функцию (классический TDD — слишком дорого по токенам), а на модуль целиком.

**Цикл:**
1. Написать тесты ключевых сценариев модуля (успешные пути, edge cases, ошибки)
2. Написать реализацию
3. Прогнать тесты — зелёные → коммит, красные → фиксить → повтор

**Почему это критично для agent-first:**
- В AF ревью реже → тесты = главный safety net
- Тест однозначнее словесного описания — агент не уйдёт в сторону
- При рефакторинге тесты показывают что поведение не сломалось
- YAML-манифесты проверяют структуру, тесты проверяют поведение — вместе покрывают всё

**Регистрация:** команды запуска тестов указываются в `project.yaml → tests`, чтобы агент знал что запускать.

### 9.5. Всегда использовать Feature-Based Architecture для организации кода

Код группируется по бизнес-назначению, не по техническому типу. Всё что относится к одной фиче — в одной папке.

**Структура проекта:**
- `features/` (или `modules/`) — одна папка на бизнес-возможность
- `shared/` — только код, используемый в 2+ фичах
- Каждая папка фичи содержит свои компоненты, хуки/сервисы, типы, тесты

**Правила:**
- Всё, относящееся к фиче, лежит в её папке (принцип колокации)
- Фичи импортируют друг друга только через index.ts (публичный API)
- Выноси в shared/ только когда реально используется в 2+ фичах, не заранее
- Тесты рядом с кодом (features/orders/orders.test.ts), не в отдельной папке tests/

**Как определить границы фичи:**
- Тест: "Можно описать одним предложением для пользователя?"
- "Пользователь может управлять корзиной" → одна фича (cart)
- "Пользователь может нажать кнопку" → слишком мелко, часть фичи
- "Пользователь может пользоваться магазином" → слишком крупно, разбивай

**Анти-паттерны:**
- Layer-based группировка (controllers/, services/, models/) — размазывает фичу по папкам
- Преждевременный shared/ — вынос "на всякий случай" до 2+ использований
- Прямые импорты из внутренностей чужой фичи, минуя index.ts
- Папка shared/ больше чем features/ — признак что всё складывают в общее

**Почему это критично для agent-first:**
- Агент видит весь контекст фичи в одной папке — меньше файлов для координации
- Меньше шансов забыть обновить связанный файл в другой папке
- Предсказуемая структура — агент знает куда класть новый код
- Merge-конфликты реже — разные фичи не пересекаются по папкам

### Как пять правил работают вместе

```
context7 даёт актуальные знания
  → sequential-thinking структурирует решение
    → Feature-Based Architecture задаёт структуру проекта
      → Test-First фиксирует ожидаемое поведение
        → KISS/DRY/SOLID задают стандарт реализации
          → Self-Check верифицирует все правила перед коммитом
```

Код сразу пишется качественно, в правильной структуре, с гарантией поведения. Self-Check в конце цикла ловит нарушения, которые проскочили в процессе.

---

## Приоритет внедрения (порядок действий)

Не делай всё сразу:

1. **Шаг 1:** один YAML-манифест на самый активный слой + `validate.py` + pre-commit. Обкатай на одной части.
2. **Шаг 2:** через неделю работы — если зашло, расширь на остальные слои + `project.yaml`.
3. **Шаг 3:** ADR — заводи первый **когда реально принимаешь решение**.
4. **Шаг 4:** autonomy rules в CLAUDE.md — когда накопится 3-5 повторяющихся проблем.
5. **Шаг 5:** observability в `project.yaml` — когда начнёшь использовать агента для прод-багов.

---

## Чеклист старта на новом проекте

- [ ] Создать `documentation/project.yaml` (даже минимальный)
- [ ] Создать манифест самого активного слоя (`frontend.yaml` или `backend.yaml`)
- [ ] Написать `validate.py` (~100 строк)
- [ ] Добавить `.pre-commit-config.yaml` с вызовом validate
- [ ] Обновить `CLAUDE.md`: секции "Agent entry points" и "Autonomy rules"
- [ ] Первый ADR (хотя бы "почему выбран такой стек")
- [ ] Скрипт `scripts/validate.sh` который вызывает всё разом

---

## Что НЕ делать

- ❌ Писать MD-описания блоков параллельно с YAML (двойная синхронизация)
- ❌ Поддерживать диаграмму вручную как источник данных
- ❌ Настраивать автогенерацию манифеста до появления боли
- ❌ Писать ADR задним числом на 20 решений сразу
- ❌ Настраивать CI раньше pre-commit
- ❌ Детализировать autonomy rules заранее — дополняй по мере реальных случаев

---

# Приложение А: Готовые шаблоны

Копируй-вставляй в новый проект.

## А.1. Минимальный `documentation/project.yaml`

```yaml
# Super-index for the project. Agents start reading from here.
meta:
  name: my-project
  created: 2026-04-05

layers:
  # Добавляй по мере создания манифестов
  # frontend: documentation/frontend.yaml
  # backend: documentation/backend.yaml

key_files:
  # Критичные точки входа в код
  # entrypoint: src/main.py
  # config: src/config.py

env:
  required: []
  optional: []

tests:
  # smoke: pytest tests/smoke/
  run_before_merge: []

observability:
  # logs:
  # health_check:
```

## А.2. Минимальный `documentation/frontend.yaml`

```yaml
# Map of frontend blocks
blocks:
  example-block:
    code_path: src/features/example
    entry: index.ts
    summary: "Short 1-line description"
    depends_on: []
    related_blocks: []
    api_calls: []
    adr: []
    gotchas: []
    notes: |
      Extended context why it works this way.
```

## А.3. Готовый `documentation/validate.py`

```python
#!/usr/bin/env python3
"""Validates project documentation manifests against filesystem + cross-refs."""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "documentation"
ADR_DIR = DOCS / "adr"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_all_blocks() -> dict:
    """Load all layer manifests. Returns {block_name: (layer_file, block_data)}."""
    project = load_yaml(DOCS / "project.yaml")
    all_blocks = {}
    for layer_name, layer_path in (project.get("layers") or {}).items():
        layer = load_yaml(ROOT / layer_path)
        for block_name, block_data in (layer.get("blocks") or {}).items():
            if block_name in all_blocks:
                print(f"WARN: duplicate block '{block_name}' across layers")
            all_blocks[block_name] = (layer_path, block_data)
    return all_blocks


def collect_adr_files() -> dict:
    """Returns {adr_number: (path, affects_list)}."""
    if not ADR_DIR.exists():
        return {}
    adrs = {}
    for adr_file in ADR_DIR.glob("*.md"):
        name = adr_file.stem  # e.g. "004-client-side-filtering"
        try:
            num = int(name.split("-")[0])
        except (ValueError, IndexError):
            continue
        affects = []
        with open(adr_file, encoding="utf-8") as f:
            for line in f:
                if line.lower().startswith("affects:"):
                    raw = line.split(":", 1)[1].strip().strip("[]")
                    affects = [x.strip() for x in raw.split(",") if x.strip()]
                    break
        adrs[num] = (adr_file, affects)
    return adrs


def validate() -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    all_blocks = collect_all_blocks()
    all_adrs = collect_adr_files()

    # 1. code_path + entry must exist
    for block_name, (layer, block) in all_blocks.items():
        code_path_str = block.get("code_path", "")
        if not code_path_str:
            errors.append(f"{block_name}: code_path is empty")
            continue
        code_path = ROOT / code_path_str
        if not code_path.exists():
            errors.append(f"{block_name}: code_path not found: {code_path_str}")
            continue
        entry_str = block.get("entry", "")
        if not entry_str:
            errors.append(f"{block_name}: entry field is missing")
            continue
        entry = code_path / entry_str
        if not entry.exists():
            errors.append(f"{block_name}: entry not found: {entry_str}")

    # 2. depends_on / related_blocks point to existing blocks
    for block_name, (_, block) in all_blocks.items():
        for ref_field in ("depends_on", "related_blocks"):
            for ref in block.get(ref_field, []) or []:
                if ref not in all_blocks:
                    errors.append(f"{block_name}.{ref_field}: unknown block '{ref}'")

    # 3. adr: [N] must point to existing ADR files
    for block_name, (_, block) in all_blocks.items():
        for adr_num in block.get("adr", []) or []:
            if adr_num not in all_adrs:
                errors.append(f"{block_name}.adr: ADR-{adr_num:03d} file not found")

    # 4. ADR Affects: must match block.adr (two-way consistency)
    for adr_num, (adr_path, affects) in all_adrs.items():
        for block_ref in affects:
            if block_ref not in all_blocks:
                errors.append(f"ADR-{adr_num:03d} Affects unknown block: {block_ref}")
                continue
            block_adr = all_blocks[block_ref][1].get("adr", []) or []
            if adr_num not in block_adr:
                errors.append(
                    f"ADR-{adr_num:03d} lists '{block_ref}' in Affects, "
                    f"but block doesn't reference adr: [{adr_num}]"
                )

    # 5. Warnings for empty critical fields
    for block_name, (_, block) in all_blocks.items():
        summary = block.get("summary", "") or ""
        if not summary or "TODO" in summary.upper():
            warnings.append(f"{block_name}: summary is empty or TODO")

    # 6. Orphan detection — folders not covered by any manifest block
    covered_paths = set()
    parent_dirs = set()
    for block_name, (_, block) in all_blocks.items():
        cp = block.get("code_path", "")
        if cp:
            covered_paths.add(Path(cp).as_posix())
            parent_dirs.add(Path(cp).parent.as_posix())

    for parent in parent_dirs:
        parent_path = ROOT / parent
        if not parent_path.exists():
            continue
        for child in sorted(parent_path.iterdir()):
            if not child.is_dir():
                continue
            relative = child.relative_to(ROOT).as_posix()
            if relative not in covered_paths:
                warnings.append(f"orphan: {relative} not in any manifest block")

    return errors, warnings


if __name__ == "__main__":
    errors, warnings = validate()
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("OK: all manifests valid")
```

## А.4. Готовый `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: docs-sync
        name: Validate documentation manifests
        entry: python documentation/validate.py
        language: system
        pass_filenames: false
        always_run: true
```

**Установка после создания файла:**
```bash
pip install pre-commit
pre-commit install
```

## А.5. Готовый `scripts/validate.sh`

```bash
#!/usr/bin/env bash
set -e

echo "==> Validating documentation manifests..."
python documentation/validate.py

# Add more checks here as project grows:
# echo "==> Running linters..."
# echo "==> Running type checks..."
# echo "==> Running smoke tests..."

echo "OK: all checks passed"
```

Не забудь: `chmod +x scripts/validate.sh`

## А.6. Готовый шаблон ADR `documentation/adr/001-example.md`

```markdown
# ADR 001: Short decision title
Status: accepted
Date: 2026-04-05
Affects: []

## Context
What problem we are solving and why it matters now.

## Decision
What we decided and how it will be implemented.

## Consequences
+ Positive outcomes
- Trade-offs and limitations
- Migration path if superseded
```

## А.7. Готовые секции для `CLAUDE.md`

```markdown
## Agent entry points
ALWAYS start here when working on this project:
1. Read `documentation/project.yaml` to get the map
2. Based on task, read relevant layer YAML (e.g. `documentation/frontend.yaml`)
3. Use `code_path` + `entry` from manifest to jump directly to code
4. Do NOT grep the entire repo — use the manifest

## When refactoring
1. Update corresponding YAML manifest if paths/summary changed
2. Run `python documentation/validate.py`
3. Pre-commit hook enforces this automatically

## Agent autonomy rules

### Do without asking:
- Читать код
- Запускать `scripts/validate.sh`
- Обновлять YAML после рефакторинга
- Создавать новые ADR при принятии решений

### Ask before:
- Удалять файлы
- Менять схему БД (migrations)
- Трогать .env или config
- Деплоить в прод
- Менять существующие ADR (они append-only)

### Never do:
- push --force
- Коммитить secrets / .env
- Менять ADR задним числом (создавай новый с "supersedes N")

## Self-maintaining documentation rules

### When editing a block:
1. Before changes: read its gotchas and notes in the YAML manifest
2. **LIST all gotchas to the user** before starting implementation — never skip silently
3. If you discover a non-trivial detail during work that future agent
   should know — ADD IT to gotchas
4. If you make architectural decision — create ADR and link in adr: []

### When reading code reveals a "footgun":
- Add a short gotcha to the block in YAML
- Format: "Don't X — reason Y" (one sentence)

### Budget: add at most 1-2 gotchas per session
Don't spam the manifest — only genuinely important things.
```

### Правила безопасного обновления CLAUDE.md

Критично для проектов где уже есть `CLAUDE.md` с важным контентом:

**Поведение при обновлении:**
- ✅ Если `CLAUDE.md` существует → **дописать** секции в конец или после раздела обзора проекта
- ✅ **Не перезаписывать** существующий контент
- ✅ **Не дублировать** секции если они уже есть (проверять по тексту заголовков)
- ✅ Если файла нет → создать с нуля из шаблона
- ✅ Показать пользователю **diff** и дождаться подтверждения перед сохранением

**Куда вставлять секции:**
- В начало файла (после обзора проекта), чтобы агент видел их первыми
- Перед секциями с командами разработки
- После секций с метаинформацией проекта (если есть)

**Почему показывать diff:**
`CLAUDE.md` часто содержит персональные настройки, команды, custom-инструкции пользователя. Перезапись без подтверждения — худшее что может сделать агент. Всегда показывай изменения и жди OK.

**Секции для добавления** (из шаблона выше):
- `## Agent entry points`
- `## When refactoring`
- `## Agent autonomy rules`
- `## Self-maintaining documentation rules` (из Приложения Г.9)

---

# Приложение Б: Внедрение в существующий проект

Если проект уже большой — не пытайся задокументировать всё сразу.

## Стратегия "точка боли"

**Начни с одного слоя который чаще всего трогается агентом.**

Обычно это:
- самый активный модуль (фронт или часто меняющийся бэк-сервис)
- часть где больше всего "забывается контекст" при рефакторинге

## Пошаговый процесс

### Шаг 1: Инвентаризация (1-2 часа)
Попроси агента просканировать выбранный слой и выдать список блоков:

> "Просканируй `src/features/` и предложи разбиение на блоки для YAML-манифеста. Для каждого укажи code_path, главный entry-файл и 1 строку summary."

Получишь черновик — скорректируй вручную.

### Шаг 2: Создание манифеста (30 минут)
На основе инвентаризации создай `documentation/<layer>.yaml`. Заполни только обязательные поля (`code_path`, `entry`, `summary`). Остальное — по мере работы.

### Шаг 3: Валидатор + pre-commit (30 минут)
Копируешь шаблоны из Приложения А. Запускаешь, смотришь что упадёт. Чинишь.

### Шаг 4: Обновить CLAUDE.md (10 минут)
Добавляешь секции Entry points + Autonomy rules из Приложения А.7.

### Шаг 5: Обкатка 1-2 недели
**Не добавляй ничего нового.** Работаешь как обычно. Замечаешь:
- Какие поля хочется дозаполнить (`gotchas`, `notes`)
- Какие блоки забывал обновлять после рефакторинга
- Где валидатор реально помог

### Шаг 6: Решение о расширении
- Зашло → делаешь `project.yaml` + манифест для следующего слоя
- Не зашло → разбираешься почему. Часто проблема в том что блоки нарезаны слишком мелко или слишком крупно.

## Чего избегать при миграции

- **Не документировать всё разом.** Попытка создать манифесты на 50+ блоков за раз = 3 дня работы и потом никто не поддерживает
- **Не создавать ADR ретроспективно** для всех прошлых решений. Только для новых, начиная с момента внедрения
- **Не переписывать существующую документацию.** Старые README и MD-файлы оставь как есть, просто не добавляй новые

## Особый случай: монорепо / микросервисы

Если в проекте несколько независимых сервисов — делай **отдельный `project.yaml` для каждого**:

```
services/
├── auth-service/
│   └── documentation/
│       ├── project.yaml
│       └── validate.py
├── billing-service/
│   └── documentation/
│       ├── project.yaml
│       └── validate.py
```

А в корне репо — `documentation/meta.yaml` со ссылками на сервисы:

```yaml
services:
  auth: services/auth-service/documentation/project.yaml
  billing: services/billing-service/documentation/project.yaml
```

Общий `validate.py` в корне проходит по всем сервисам.

---

# Приложение В: Troubleshooting

## Проблема: pre-commit не срабатывает при коммите

**Симптомы:** коммит проходит без запуска валидатора.

**Причины и решения:**
1. Не установлен hook → `pre-commit install`
2. Коммитишь через `--no-verify` → убери этот флаг
3. Коммитишь через веб-интерфейс GitHub → настрой CI (Уровень 3)
4. Репо клонирован, но `pre-commit install` не запускался на этой машине → запусти

**Проверка:**
```bash
cat .git/hooks/pre-commit
# Должен содержать ссылку на pre-commit framework
```

## Проблема: validate.py падает на рабочем коде

**Симптомы:** код работает, но валидатор ругается.

**Частые причины:**
1. **Путь с backslash на Windows в YAML** — YAML должен содержать forward slashes: `src/features/auth`, не `src\features\auth`
2. **Относительный путь некорректен** — `code_path` должен быть относительно корня репо, не от `documentation/`
3. **entry-файл указан с расширением которого нет** — проверь что `BotsList.tsx` существует, а не `BotsList.ts`
4. **Блок в `depends_on` не существует в манифесте** — опечатка в имени блока

**Отладка:**
```bash
python documentation/validate.py
# Читай конкретные ошибки, они показывают путь
```

## Проблема: YAML-синтаксис сломался

**Симптомы:** `yaml.scanner.ScannerError` или подобное.

**Частые ошибки:**
- Таб вместо пробелов (YAML требует пробелы)
- Строка с двоеточием без кавычек: `summary: CRUD: bots` → `summary: "CRUD: bots"`
- Неправильный отступ в многострочном `notes: |`

**Быстрая проверка синтаксиса:**
```bash
python -c "import yaml; yaml.safe_load(open('documentation/frontend.yaml'))"
```

## Проблема: валидатор жалуется на двустороннюю связь ADR

**Симптомы:** `ADR-004 lists 'bots-list' in Affects, but block doesn't reference adr: [4]`

**Решение:** либо добавь `adr: [4]` в блок, либо убери блок из `Affects:` в ADR. Связь должна быть двусторонней.

## Проблема: агент всё равно не читает манифесты

**Симптомы:** агент грепает весь репо вместо использования `project.yaml`.

**Причины:**
1. В `CLAUDE.md` нет секции "Agent entry points" — добавь из Приложения А.7
2. Секция есть, но слишком длинная и агент её пропускает — поставь в начало файла
3. Манифесты недостаточно полные — если в YAML нет нужной инфы, агент идёт искать в коде. Обогащай `gotchas` и `api_calls`.

## Проблема: pre-commit тормозит коммиты

**Симптомы:** `validate.py` выполняется > 2 сек.

**Решения:**
1. Кэшировать результат если манифесты не менялись
2. Запускать validate.py только если менялись файлы в `documentation/` или изменялась структура папок — через `files:` паттерн в pre-commit
3. Перенести тяжёлые проверки в CI, в pre-commit оставить только базовые

Пример с фильтром по изменённым файлам:
```yaml
- id: docs-sync
  entry: python documentation/validate.py
  language: system
  files: '^(documentation/.*|.*/index\.(ts|tsx|js|jsx|py))$'
  pass_filenames: false
```

## Проблема: блоки стали слишком большими / слишком мелкими

**Симптомы:** один блок описывает 50 файлов, или наоборот блоков стало 200+.

**Правило большого пальца:**
- Блок = фича/модуль с чёткой границей ответственности
- Обычно совпадает с папкой на 2-3 уровне от корня (например `src/features/auth/`)
- Если блок > 15 файлов — рассмотри разбиение на под-блоки
- Если блоков > 40 на слой — возможно уровень нарезки слишком детальный

## Проблема: забываю обновить манифест

**Симптомы:** переместил папку — pre-commit ругается.

**Это нормально.** Это ровно та ситуация, против которой построена система. Обновить манифест — единственное правильное действие. Со временем вырабатывается рефлекс.

Если забывание повторяется постоянно — см. Приложение Г (автоматизация дисциплины).

---

# Приложение Г: Автоматизация дисциплины

Механизмы которые снимают с тебя ручную работу по поддержанию манифестов.

## Г.1. Матрица "что можно автоматизировать"

| Проблема | Автоматизация | Эффект |
|---|---|---|
| Забыл обновить путь | validate.py + pre-commit | 100% |
| Создал папку, не добавил в YAML | Детектор сирот | 100% |
| Писать заготовку блока вручную | scripts/add_block.py | 80% экономии |
| Пустой summary / entry | Warning в валидаторе | 100% |
| Устаревшие api_calls | Авто-парсинг axios/fetch | 90% |
| Устаревшие depends_on | Авто-парсинг импортов | 95% |
| Документация отстала от кода | Stale-детектор по mtime | 70% (sanity) |
| Новая фича без структуры | scripts/new_block.py | 90% |
| Пустые gotchas | Правило "агент дополняет по ходу" | 50% |
| Архитектурные решения | Не автоматизируется | 0% |

## Г.2. Детектор сирот (встроен в validate.py)

Уже встроен в `validate.py` (проверка #6). Автоматически сканирует parent-директории всех `code_path` и выдаёт warning на папки, не описанные ни в одном блоке.

Не требует ручной настройки `features_root` — определяет нужные директории из самих манифестов.

## Г.3. Warning на пустые критичные поля (встроен в validate.py)

Уже встроен в `validate.py` (проверка #5). Выдаёт warning если `summary` пустой или содержит TODO. Warnings не блокируют коммит, но видны → неудобство мотивирует заполнить.

## Г.4. Stale-детектор (код обновлялся, а YAML нет)

```python
import os

def detect_stale_blocks(all_blocks, threshold_days=90) -> list[str]:
    warnings = []
    for name, (layer_path, block) in all_blocks.items():
        code_path = ROOT / block.get("code_path", "")
        if not code_path.exists():
            continue
        yaml_mtime = os.path.getmtime(ROOT / layer_path)
        code_mtime = max(
            (os.path.getmtime(f) for f in code_path.rglob("*") if f.is_file()),
            default=0,
        )
        days_diff = (code_mtime - yaml_mtime) / 86400
        if days_diff > threshold_days:
            warnings.append(
                f"STALE: {name}: code updated {int(days_diff)}d after YAML last touch"
            )
    return warnings
```

Sanity-чек: напоминает что пора пересмотреть notes/gotchas.

## Г.5. scripts/add_block.py — заготовка блока

```python
#!/usr/bin/env python3
"""Add a skeleton block entry to the appropriate YAML manifest."""
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).parent.parent

def add_block(folder_path: str, manifest_name: str = "frontend"):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"ERROR: {folder} does not exist")
        sys.exit(1)

    # Автодетект entry-файла
    candidates = ["index.ts", "index.tsx", "index.js", "__init__.py", "main.py"]
    entry = None
    for c in candidates:
        if (folder / c).exists():
            entry = c
            break
    if not entry:
        # Взять первый файл в папке
        files = [f.name for f in folder.iterdir() if f.is_file()]
        entry = files[0] if files else "TODO"

    block_name = folder.name
    manifest_path = ROOT / "documentation" / f"{manifest_name}.yaml"

    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {"blocks": {}}

    data.setdefault("blocks", {})[block_name] = {
        "code_path": str(folder.relative_to(ROOT)).replace("\\", "/"),
        "entry": entry,
        "summary": "TODO: fill in",
        "depends_on": [],
        "related_blocks": [],
        "api_calls": [],
        "adr": [],
        "gotchas": [],
        "notes": "",
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"Added block '{block_name}' to {manifest_name}.yaml")
    print(f"Don't forget to fill in summary and gotchas!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_block.py <folder_path> [manifest_name]")
        sys.exit(1)
    add_block(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "frontend")
```

Использование:
```bash
python scripts/add_block.py src/features/notifications
# → добавляет заготовку в frontend.yaml
```

## Г.6. Авто-парсинг api_calls (для фронта)

```python
import re
from pathlib import Path

API_PATTERNS = [
    r'axios\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
    r'fetch\([\'"]([^\'"]+)[\'"].*?method:\s*[\'"](\w+)[\'"]',
    r'api\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
]

def extract_api_calls(code_path: Path) -> list[str]:
    calls = set()
    for file in code_path.rglob("*.ts*"):
        content = file.read_text(encoding="utf-8", errors="ignore")
        for pattern in API_PATTERNS:
            for match in re.finditer(pattern, content):
                method = match.group(1).upper()
                url = match.group(2)
                calls.add(f"{method} {url}")
    return sorted(calls)
```

Вызывается в скрипте который обновляет поле `api_calls` во всех блоках. Запускаешь раз в неделю:
```bash
python scripts/sync_api_calls.py
```

## Г.7. Авто-парсинг depends_on (для фронта с алиасами)

```python
def extract_dependencies(code_path: Path, alias_map: dict) -> list[str]:
    """alias_map: {'@/features/': 'block_prefix'} для резолва алиасов"""
    deps = set()
    import_re = re.compile(r'from\s+[\'"]([^\'"]+)[\'"]')
    for file in code_path.rglob("*.ts*"):
        content = file.read_text(encoding="utf-8", errors="ignore")
        for match in import_re.finditer(content):
            imp = match.group(1)
            if imp.startswith("@/features/"):
                block = imp.split("/")[2]  # @/features/auth/... → auth
                deps.add(block)
    return sorted(deps)
```

Аналогично — запускаешь периодически или из pre-commit.

## Г.8. scripts/new_block.py — создать фичу с нуля

Комбинирует создание папки + шаблонных файлов + запись в YAML + ADR-заготовку:

```python
#!/usr/bin/env python3
"""Scaffold a new feature block: folder + files + YAML entry + optional ADR."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def new_block(name: str, with_adr: bool = False):
    folder = ROOT / "src" / "features" / name
    if folder.exists():
        print(f"ERROR: {folder} already exists")
        sys.exit(1)

    folder.mkdir(parents=True)
    (folder / "index.ts").write_text(f"// {name} block entry point\n")
    (folder / f"{name.capitalize()}.tsx").write_text(
        f"export const {name.capitalize()} = () => null;\n"
    )

    # Add to manifest
    import subprocess
    subprocess.run(["python", "scripts/add_block.py", str(folder)], check=True)

    # Create ADR placeholder
    if with_adr:
        adr_dir = ROOT / "documentation" / "adr"
        existing = list(adr_dir.glob("*.md"))
        next_num = max((int(f.stem.split("-")[0]) for f in existing), default=0) + 1
        adr_file = adr_dir / f"{next_num:03d}-{name}-design.md"
        adr_file.write_text(
            f"# ADR {next_num:03d}: {name} design\n"
            f"Status: draft\nAffects: [{name}]\n\n"
            "## Context\nTODO\n\n## Decision\nTODO\n\n## Consequences\nTODO\n"
        )
        print(f"Created ADR: {adr_file.name}")

    print(f"New block '{name}' scaffolded at {folder}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/new_block.py <name> [--with-adr]")
        sys.exit(1)
    new_block(sys.argv[1], "--with-adr" in sys.argv)
```

## Г.9. Правила в CLAUDE.md — самодополнение gotchas

Добавить в `CLAUDE.md`:

```markdown
## Self-maintaining documentation rules

### When editing a block:
1. Before changes: read its gotchas and notes in the YAML manifest
2. If you discover a non-trivial detail during work that future agent
   should know — ADD IT to gotchas
3. If you make architectural decision — create ADR and link in adr: []

### When reading code reveals a "footgun":
- Add a short gotcha to the block in YAML
- Format: "Don't X — reason Y" (one sentence)
- Examples:
  - "Don't remove useMemo — critical for perf on 1k+ items"
  - "API returns stale data 5s (Redis cache)"

### Budget: add at most 1-2 gotchas per session
Don't spam the manifest — only genuinely important things.
```

Теперь агент **сам** дополняет документацию по ходу работы, без твоих указаний.

## Г.10. Scheduled-задачи для периодических проверок

Если используешь CI (Уровень 3) — можно настроить еженедельный запуск:

```yaml
# .github/workflows/docs-health.yml
name: Docs Health Check
on:
  schedule:
    - cron: '0 9 * * 1'  # каждый понедельник 9:00 UTC
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml
      - run: python documentation/validate.py
      - name: Stale blocks check
        run: python documentation/check_stale.py
```

Результаты приходят в Issues или Slack → видишь накопившиеся проблемы.

## Г.11. Приоритет внедрения автоматизации

**Немедленно (при начальной настройке):**
- Детектор сирот (Г.2) — 10 строк в validate.py
- Warning на пустые поля (Г.3) — 10 строк
- Правила в CLAUDE.md про самодополнение (Г.9)

**Когда накопится 15-20 блоков:**
- scripts/add_block.py (Г.5)
- Stale-детектор (Г.4)

**Когда API часто меняется:**
- Авто-парсинг api_calls (Г.6)
- Авто-парсинг depends_on (Г.7)

**Для больших проектов (50+ блоков):**
- scripts/new_block.py (Г.8)
- Scheduled CI (Г.10)

**Главный принцип:** автоматизируй **по мере боли**, не заранее. Каждая автоматизация = код который надо поддерживать.

---

# Приложение Д: Как использовать этот гайд

Операционные инструкции: как работать с системой на практике.

## Д.1. Сценарии использования

### Сценарий А: Новый проект с нуля
1. Создаёшь проект (git init, выбираешь стек)
2. Копируешь `agent-first-guide.md` в `documentation/`
3. Идёшь в раздел "Чеклист старта на новом проекте"
4. Берёшь готовые шаблоны из Приложения А
5. За 30-60 минут — базовый setup готов
**Твоя роль:** следуешь инструкции.

### Сценарий Б: Существующий проект
1. Файл уже лежит в `documentation/agent-first-guide.md`
2. Идёшь в Приложение Б "Миграция существующего проекта"
3. Следуешь Шагам 1-6 (инвентаризация → манифест → валидатор → обкатка)
4. Через 1-2 недели решаешь — расширять или откатить
**Твоя роль:** выбираешь стартовый слой, принимаешь решение после обкатки.

### Сценарий В: Проблема в процессе работы
1. Открываешь Приложение В "Troubleshooting"
2. Находишь похожий симптом
3. Применяешь решение

### Сценарий Г: Агент не помогает как хотелось
1. Идёшь в Приложение Г "Автоматизация дисциплины"
2. Добавляешь нужные механизмы (детектор сирот, warning'и, и т.д.)

## Д.2. Разделение обязанностей: агент vs ты

### Агент делает:
- Читает код
- Сканирует структуру проекта
- Копирует и адаптирует шаблоны
- Создаёт манифесты по инструкциям
- Обновляет YAML при рефакторинге
- Запускает валидаторы
- Оформляет ADR по твоему диктованию

### Ты делаешь:
- Определяешь **границы блоков**
- Заполняешь `gotchas` (контекст в твоей голове)
- **Принимаешь** архитектурные решения
- **Диктуешь** содержание ADR
- Решаешь **когда** переходить на следующий уровень автоматизации
- Ревьюишь результат

## Д.3. Когда нужны твои архитектурные решения

### Решение 1: Границы блоков
**Когда:** при первой инвентаризации.
**Вопросы:** `auth` и `user-profile` — один блок или два? `api-client` — отдельный блок или часть каждой фичи?
**Правило:** блок = папка на 2-3 уровне + чёткая граница ответственности + 5-15 файлов.

### Решение 2: Что попадает в gotchas
**Когда:** при работе над блоком, когда встречается нетривиальное место.
**Источник:** твой опыт. Агент не знает прошлых багов, перф-тестов, забытых требований.
**Пример:** "Не упрощать useMemo — лагает на 500+ элементах".

### Решение 3: Создание ADR
**Триггеры:**
- Выбираешь между 2+ подходами (OAuth vs JWT)
- Меняешь существующее решение
- Решаешь "почему НЕ делать Y"

**Процесс:** ты принимаешь решение → диктуешь контекст → агент оформляет файл.

### Решение 4: Куда положить новую фичу
**Когда:** запрос "добавь новую фичу".
**Вопросы:** отдельный блок или часть существующего? Клиентский стейт или серверный? Свой API или общий?

### Решение 5: Когда переходить на следующий уровень автоматизации
**Когда:** периодически (раз в месяц/квартал).
**Где искать:** раздел "Уровни автоматизации" + Приложение Г.

### Решение 6: Стратегические изменения структуры
**Симптомы:**
- Блоков стало 60+ на слой → пора вводить категории или сплитить layer
- Манифест вырос до 1000 строк → пора разбивать
- Появились микросервисы → переход на multi-repo

## Д.4. Типичные задачи и диалоги

### Задача: мелкая правка (стиль, текст)
```
Ты: "Измени цвет кнопки в BotsList на синий"
Агент: читает project.yaml → frontend.yaml → block bots-list
       → открывает entry-файл → правит → коммитит
Ты: approve
```
**Участие:** 0 архитектурных решений.

### Задача: изменение логики
```
Ты: "Добавь серверную фильтрацию в список ботов"
Агент: читает block bots-list → видит gotcha "Фильтрация клиентская — ADR-004"
       → читает ADR-004
       → ОСТАНАВЛИВАЕТСЯ: "ADR-004 говорит обратное. Меняем подход?"
Ты: "Да, теперь у клиентов > 500 ботов. Создай ADR-015 supersedes 004."
Агент: создаёт ADR, обновляет блок, реализует
```
**Участие:** 1 решение.

### Задача: новая фича
```
Ты: "Добавь push-уведомления"
Агент: "Отдельный блок или в settings? Свой стейт или общий?"
Ты: принимаешь решения
Агент: создаёт структуру (new_block.py), оформляет ADR-заготовку
Ты: диктуешь содержание ADR
Агент: реализует + обновляет манифест
```
**Участие:** 3-5 решений.

### Задача: рефакторинг
```
Ты: "Объедини auth и user-profile в один блок"
Агент: "Это меняет границы блоков. Затронет X связанных блоков. Продолжать?"
Ты: confirm
Агент: выполняет, обновляет все ссылки в YAML и ADR
Валидатор: проверяет что ничего не разъехалось
```
**Участие:** 1 решение + ревью.

## Д.5. Как формулировать запрос агенту

### Правильный запрос — новый проект
```
Настрой этот проект согласно documentation/agent-first-guide.md.
Стек: <Python/FastAPI + React/Vite/...>
Первичный слой: <frontend>
Структура кода: <src/features/ или web/frontend/src/features/>

Используй чеклист старта. На этапе определения блоков покажи
черновик для ревью ПЕРЕД созданием манифеста.
```

### Правильный запрос — существующий проект
```
Внедри подход из documentation/agent-first-guide.md.
Следуй Приложению Б — миграция существующего проекта.
Начни со Шага 1 (инвентаризация) для слоя <frontend>.
Путь к коду: <web/frontend/src/features/>

ОСТАНОВИСЬ после Шага 2 (создание манифеста).
Мне нужно проверить разбиение на блоки перед продвижением.
```

### Типичные ошибки запроса

**❌ Слишком общий:**
> "Настрой всё по agent-first"

Результат: агент не останавливается на архитектурных решениях, нарезает блоки как удобно.

**❌ Без контекста стека:**
> "Следуй гайду"

Результат: дефолтные пути из шаблонов, не совпадают с твоим проектом.

**❌ "Сделай сразу всё":**
> "Настрой гайд, создай все слои, заполни все поля"

Результат: куча TODO-плейсхолдеров, работы потом на неделю.

### Чеклист правильного запроса
- [ ] Указан стек
- [ ] Указан первичный слой (ОДИН, не все сразу)
- [ ] Указан путь к коду
- [ ] Запрошена остановка на ключевых точках (границы блоков)

## Д.6. Чеклист после первичной настройки

После того как агент закончил setup, ТЫ обязательно:

- [ ] Запускаешь `pre-commit install` (если не сделал агент)
- [ ] Запускаешь `python documentation/validate.py` — должно быть "OK"
- [ ] Открываешь сгенерированный манифест и проверяешь:
  - [ ] Все блоки на месте
  - [ ] Нет перекосов в именовании
  - [ ] Summary у 3-5 критичных блоков написан осмысленно (не TODO)
- [ ] Делаешь тестовый коммит — проверяешь что pre-commit срабатывает
- [ ] Если что-то не так → идёшь в Приложение В (Troubleshooting)

## Д.7. Главная мысль

**Файл — не документация для одноразового чтения.**
Это **операционный справочник** к которому возвращаешься:
- При старте нового проекта
- При возникновении проблемы
- При принятии решения о расширении системы
- При onboarding'е нового человека или агента

Со временем рефлексы выработаются, и открывать файл будешь реже.
Но справочник остаётся на случай нестандартной ситуации.

**Твоя роль в agent-first проекте:** архитектор + хранитель контекста.
**Агент делает всё остальное.**

---

# Приложение Е: Workflow новой фичи

Как внедрять новую фичу в AF-проекте. Описывает порядок действий агента и пользователя, когда поступает запрос на новую функциональность.

## Е.1. Чеклист новой фичи (9 шагов)

```
[ ] 1. Прочитать documentation/project.yaml → найти затронутые слои
[ ] 2. Прочитать YAML затронутых блоков: summary, gotchas, notes, related_blocks
[ ] 3. Задать вопрос: "есть ли несколько разумных путей реализации?"
      ├── Да  → создать ADR ДО реализации, линковать в блок через adr: [N]
      └── Нет → просто реализация
[ ] 4. Написать тесты ключевых сценариев модуля ДО реализации
[ ] 5. Реализовать фичу, прогнать тесты (зелёные → дальше, красные → фиксить)
[ ] 6. Обновить YAML затронутых блоков (если поменялась суть/структура):
       - code_path/entry (если перемещал файлы)
       - summary (если сменилось назначение блока)
       - notes (если появился/удалился ключевой файл)
       - api_calls (если добавился endpoint)
       - depends_on / related_blocks (если изменились связи)
[ ] 7. Добавить gotcha (если столкнулся с неочевидной проблемой, 1-2 за сессию)
[ ] 8. Self-Check — проверить код на соответствие cross-cutting правилам:
       - [ ] context7: проверены актуальные доки для используемых библиотек?
       - [ ] KISS: нет функций > 40 строк, нет вложенности > 3 уровней?
       - [ ] DRY: grep по проекту на похожую логику, нет лишнего дублирования?
       - [ ] SOLID: каждый новый модуль/класс имеет одну ответственность?
       - [ ] Feature-Based: новый код внутри features/[название]/, не в корне?
       - [ ] Feature-Based: нет прямых импортов из внутренностей чужой фичи?
       - [ ] Feature-Based: в shared/ не добавлено ничего, что используется только 1 фичей?
       - [ ] Test-First: тесты есть и проходят для новых/изменённых модулей?
       Если что-то не так — исправить до коммита.
[ ] 9. Commit → pre-commit hook валидирует ссылки
```

## Е.2. Правило «нужен ли ADR?»

ADR заводится **только при архитектурном решении**, не на каждую фичу.

**Правило 3-х критериев** — если все три ✅, нужен ADR:

1. Рассматривается **2+ разумных варианта** реализации
2. На размышление потрачено **>10 минут**
3. Через полгода кто-то может спросить: «а почему X, а не Y?»

### Примеры

| Фича | ADR? | Почему |
|---|---|---|
| Новый endpoint `GET /api/users/{id}/export` | ❌ | Тривиальная реализация |
| Баг-фикс в validator | ❌ | Нет альтернатив |
| Изменение текста в UI | ❌ | Тривиально |
| **WebSockets vs SSE** для real-time | ✅ | Есть альтернативы |
| **Keycloak** вместо самописной auth | ✅ | Большое решение |
| **JSON-поля** в БД vs нормализация | ✅ | Trade-off |
| **Новый LLM-провайдер** через factory | ⚠️ | Зависит: если следует существующему паттерну — нет; если меняет паттерн — да |

## Е.3. Правило: ADR ДО реализации, не после

**Правильно:**
1. Принимаешь решение → пишешь ADR → линкуешь в YAML → реализуешь

**Неправильно:**
1. Реализуешь → потом задним числом пишешь ADR

Методология запрещает ретроспективные ADR (см. «Never do: Modify ADRs retroactively»).

**Если уже начал реализацию и осознал «это же выбор между X и Y»:**
- Останови работу
- Создай ADR с текущим решением
- Продолжи реализацию

## Е.4. Триггеры обновления YAML-полей

| Изменение в коде | Обновить в YAML |
|---|---|
| Переименовал/переместил файл блока | `code_path`, `entry` |
| Изменилась главная цель блока | `summary` |
| Добавил/удалил ключевой файл в блоке | `notes` |
| Добавил новый API endpoint | `api_calls` |
| Принял архитектурное решение | создать ADR + `adr: [N]` |
| Наступил на грабли | `gotchas` (1-2 за сессию) |
| Изменилась зависимость между блоками | `depends_on` / `related_blocks` |
| Создал новый блок в коде | добавить блок в YAML-манифест слоя |

## Е.5. Пример полного флоу

### Запрос: «Добавь поддержку голосовых сообщений в Telegram-бота»

```
Шаг 1-2: Ориентирование
  Агент: читает project.yaml → находит messaging-channels блок
         читает его summary, notes, gotchas
         видит related_blocks: [bot-management]

Шаг 3: Решение про ADR
  Агент: "Вариантов реализации два: OpenAI Whisper API или self-hosted Whisper.
          Это архитектурное решение → нужен ADR."
  → создаёт documentation/adr/005-voice-messages-whisper.md
  → в ADR: Affects: [messaging-channels]
  → в блоке messaging-channels: adr: [005]

Шаг 4: Реализация
  Агент: создаёт voice_handler.py, правит telegram_service.py

Шаг 5: Обновление YAML
  Агент: обновляет summary блока messaging-channels:
         "Telegram / WhatsApp / Email + voice via Whisper"
         добавляет voice_handler.py в notes

Шаг 6: Gotcha (если случилась проблема)
  Агент: наступил на грабли — добавляет gotcha:
         "Don't forward audio files — delete after transcription"

Шаг 7: Commit
  git add app/services/voice_handler.py \
          app/services/telegram_service.py \
          documentation/backend_services.yaml \
          documentation/adr/005-voice-messages-whisper.md
  git commit -m "feat: voice messages via Whisper API"
  → pre-commit: validate.py проверяет целостность ссылок ADR ↔ блок
```

## Е.6. Когда не нужен ADR (короткий чеклист)

Пропускай создание ADR если выполнено хотя бы одно:

- ✅ Есть **только один разумный способ** реализовать
- ✅ Фича следует **существующему паттерну** (например, новый endpoint по шаблону)
- ✅ Исправление бага без выбора архитектуры
- ✅ Текстовые правки, стили, мелкие улучшения UX

В этих случаях: просто реализация + обновление YAML если поменялась структура.
