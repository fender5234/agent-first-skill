# Agent-First Skill (Portable Archive)

**Версия 1.3.0** — история изменений в [`CHANGELOG.md`](CHANGELOG.md).

Проект записывает свою версию методологии в `documentation/project.yaml →
meta.af_version`. Отсутствует — значит 1.0.0. Обновляется командой
«обнови проект под AF», которая **сливает**, а не перезаписывает: проектные
проверки в `validate.py` ценнее шаблонных.

Резервная копия методологии Agent-First и скилла `agent-first-setup`.
Используется для переноса на новую машину или восстановления после потери данных.

## Что внутри

```
agent-first-skill/
├── README.md              ← этот файл
├── CHANGELOG.md           ← что менялось и почему
├── IMPROVEMENT_PLAN.md    ← бэклог доработок методологии
├── updateWorkflow.md      ← как оператор ведёт проект от ТЗ до сдачи
├── agent-first.md         ← полная методология AF (справочник)
├── AGENTS.md              ← универсальные правила для любого AI-агента
└── skill/                 ← готовый скилл для Claude Code
    ├── SKILL.md
    ├── guide.md
    ├── CHANGELOG.md       ← копия корневого; нужна маршруту апгрейда
    ├── operator-guide.md  ← руководство оператора (человека)
    └── templates/
        ├── project.yaml
        ├── layer.yaml
        ├── validate.py
        ├── check-claude-md-sections.py
    ├── check-adr-append-only.py
    ├── check-gotcha-budget.py
        ├── pre-commit-config.yaml
        ├── validate.sh
        ├── adr-template.md
        ├── claude-md-sections.md
        ├── ci-validate.yml
        ├── generate-manifest.py
        └── yaml-to-mermaid.py
```

## Файлы и их назначение

### `agent-first.md`
Полное руководство по методологии Agent-First: принципы, правила, приложения (А–Е).
Читается агентами и людьми как справочник. Не зависит от конкретного инструмента.

### `AGENTS.md`
Универсальные инструкции для AI-агентов (Cursor, Cline, Aider, Continue, Windsurf, Claude Code).
Большинство современных AI-tools автоматически читают файл `AGENTS.md` в корне проекта.
Положи копию в корень своего проекта — любой агент начнёт следовать AF-правилам.

### `skill/`
Готовый скилл `agent-first-setup` для Claude Code (CLI).
Автотриггерится по фразам: «настрой AF», «добавь фичу по AF», «проведи дрейф-аудит».
Включает `operator-guide.md` — руководство для оператора (человека), описывающее роли, точки контроля и правила взаимодействия с агентом.

---

## Как использовать на новой машине

### Вариант A: Восстановить скилл в Claude Code

```bash
# Скопировать скилл в глобальную папку скиллов Claude Code
cp -r agent-first-skill/skill ~/.claude/skills/agent-first-setup

# Теперь в Claude Code работают триггеры:
#   "настрой AF", "добавь фичу по AF", "проведи дрейф-аудит"
#   /agent-first-setup — вызов через slash-команду
```

> Путь — `~/.claude/skills/`, не `~/.claude/commands/`. Скиллы и slash-команды
> живут в разных папках; в `commands/` скилл не подхватится.

### Вариант B: Использовать с любым другим агентом

```bash
# Скопировать AGENTS.md в корень нового проекта
cp agent-first-skill/AGENTS.md /path/to/new-project/AGENTS.md

# Опционально: положить методологию в проект
mkdir -p /path/to/new-project/documentation
cp agent-first-skill/agent-first.md /path/to/new-project/documentation/agent-first-guide.md
```

Агент (Cursor / Cline / Aider / etc.) автоматически прочитает `AGENTS.md` и будет следовать правилам.

### Вариант C: Бутстрап нового проекта с нуля

1. Создай папку проекта
2. Положи `AGENTS.md` в корень
3. Положи `agent-first.md` в `documentation/agent-first-guide.md`
4. Скажи агенту: **«Настрой этот проект по AF, см. documentation/agent-first-guide.md»**
5. Агент создаст `project.yaml`, манифест слоя, `validate.py`, pre-commit hook

---

## Синхронизация содержимого

Если ты правишь методологию — обновляй **все** источники:

1. `agent-first-skill/skill/` — исходники скилла (этот архив)
2. `agent-first-skill/agent-first.md` — полная методология (должна совпадать с `skill/guide.md`)
3. `agent-first-skill/AGENTS.md` — универсальные правила для агентов
4. `~/.claude/skills/agent-first-setup/` — установленный скилл (пересобрать из `skill/`)
5. `documentation/agent-first-guide.md` — копия в текущем проекте (если есть)
6. `agent-first-skill/CHANGELOG.md` — запись о том, что и зачем изменилось
7. `agent-first-skill/skill/CHANGELOG.md` — копия предыдущего. Она едет в
   установленный скилл и нужна маршруту апгрейда: он вычисляет дельту, читая
   `CHANGELOG.md` рядом с `SKILL.md`. Без копии маршрут останавливается на первом
   шаге — так и было в 1.2.0
8. `meta.af_version` в `skill/templates/project.yaml` и в листинге Приложения А.1
9. версия в шапке этого README

Правило, которое легко нарушить: правка только в `skill/` расходится с `AGENTS.md`,
и проекты на Cursor/Cline/Aider тихо остаются на старых правилах — валидатор этого
не видит, он проверяет манифесты, а не инструкции.

Приложение А.3 в `guide.md` содержит листинг `validate.py` — он **производный** от
`skill/templates/validate.py`. При правке шаблона листинг перегенерировать, вручную
не синхронизировать.

Для пересинхронизации установленного скилла:
```bash
rm -rf ~/.claude/skills/agent-first-setup
cp -r agent-first-skill/skill ~/.claude/skills/agent-first-setup
```

Проверить, что источники не разошлись:
```bash
diff -r ~/.claude/skills/agent-first-setup agent-first-skill/skill
diff agent-first-skill/agent-first.md agent-first-skill/skill/guide.md
```

---

## Совместимость

| Инструмент | Что работает |
|---|---|
| **Claude Code** (CLI) | ✅ Полный скилл с автотриггерами + AGENTS.md |
| **Cursor** | ✅ AGENTS.md или .cursorrules |
| **Cline / Roo Code** | ✅ AGENTS.md или .clinerules |
| **Aider** | ✅ AGENTS.md или CONVENTIONS.md |
| **Continue** | ✅ AGENTS.md |
| **Windsurf** | ✅ AGENTS.md или .windsurfrules |
| **GitHub Copilot** | ⚠️ Не читает файлы конвенций, но YAML-манифесты прочитает если попросишь |
| **ChatGPT / web-агенты** | ⚠️ Нет авточтения, но можно копировать промты вручную |

---

## Связанные ресурсы

- Full methodology: `agent-first.md`
- Templates (project.yaml, validate.py, ci-validate.yml, generate-manifest.py, yaml-to-mermaid.py, и др.): `skill/templates/`
- Operator guide: `skill/operator-guide.md`
- Skill trigger phrases: `skill/SKILL.md` frontmatter
