# slimspec

[English version](README.md)

Легковесный spec-driven development для Claude Code: explore → plan → apply → verify → ground,
с обязательным red-green TDD и спеками рядом с кодом в виде модульных `CLAUDE.md`.

Дизайн и решения: [DESIGN.md](DESIGN.md).

## Установка

Склонировать репозиторий и подключить как плагин:

```bash
git clone <repo-url> ~/src/slimspec
claude --plugin-dir ~/src/slimspec
```

## Использование

```
/slimspec <идея>          # полный цикл; режим из конфига, предлагается после скана
/slimspec                 # список активных изменений и продолжение одного из них
/slimspec:fast <идея>     # старт в фиксированном режиме, без предложения режима
/slimspec:medium <идея>
/slimspec:full <идея>
```

Команды фаз, каждую можно вызвать отдельно: `/slimspec:explore`, `/slimspec:plan`, `/slimspec:apply`,
`/slimspec:verify`, `/slimspec:refine`, `/slimspec:ground`. `/slimspec <slug>` продолжает изменение
по его файлам в `.slimspec/changes/<slug>/`.

Остановок две: после explore (дизайн) и после plan. Дальше apply → verify → ground идут сами;
вопросы будут только от агентов, по дизайн-замечаниям verify или после двух автоматических
циклов исправлений.

## Режимы

| Фаза    | fast                                       | medium                         | full                                          |
|---------|--------------------------------------------|--------------------------------|-----------------------------------------------|
| explore | inline, ≤3 вопросов, вместе с plan         | scanner + grilling             | то же + явный гейт на `explore.md`            |
| plan    | секция внутри `explore.md`                 | агент planner, волны           | то же + полный `tasks.md` на гейте            |
| apply   | один implementer, TDD                      | параллельные волны             | то же                                         |
| verify  | reviewer, глубина `low`                    | reviewer, глубина `medium`     | два ревьюера (спека, код), глубина `high`     |
| ground  | обновить затронутые спеки                  | дистилляция + проверка намерения | то же + отдельный агент проверки намерения  |

TDD во всех режимах проверяется по свидетельствам red/green; TDD-хука нет.

## Конфиг

`.slimspec/config.yaml`, необязательный; у каждого ключа есть значение по умолчанию:

```yaml
mode: medium              # fast | medium | full
spec:
  format: claude-md       # claude-md | readme | central | native | none
  unit: auto              # auto (по билд-файлам) | glob директорий, напр. "src/*/"
  adr: false              # дополнительно вести решения в docs/adr/NNNN-*.md
test: auto                # или явная команда
commit: none              # none | task | wave
review:
  depth: auto             # auto (по режиму) | low | medium | high
models: {}                # переопределения по ролям: scanner, planner, implementer, reviewer, grounder
```

Модели по умолчанию: scanner — sonnet, planner — opus, implementer — sonnet, reviewer — opus, grounder — opus.
slimspec никогда не пушит.
