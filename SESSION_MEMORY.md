# Память сессии — Degg Switch (2026-08-08)

> Покажи этот файл агенту, чтобы продолжить работу.
> Всегда сверяйся с `AGENTS.md` и `SPECIFICATION.md`.

---

## 1. Что делали в этой сессии (кратко)

Нода Degg Switch ломалась при загрузке воркфлоу **внутри подграфа** (subgraph)
в воркфлоу `Krea2_MY2.json`: терялись динамические входы, на выход ничего не попадало.
Все JS-фиксы (lazy-входы, хуки `configure`, `afterConfigureGraph`, deferred rebuild)
не помогли. Диагноз: баг **не в ноде**, а во фронтенде ComfyUI (issue #12981,
регресс после фиксов «duplicate input»). Нода откачена к commit `eb7255c`,
дерево чистое. Пользователь решил остановиться, работа над нодой закрыта.

## 2. Итоговое состояние кода

- `deg_switch_node.py` — класс `DeggSwitch`: `select` (INT 1..20) + один
  optional вход `input_1`; `process()` возвращает выбранный вход через
  `kwargs.get(f"input_{select}")` (см. `deg_switch_node.py:31-34`).
- `web/js/deg_switch.js` — `rebuildInputs()` динамически добавляет/удаляет
  входы `input_N` по последнему подключённому, макс. 20, и подтягивает
  `selectWidget.options.max` (см. `deg_switch.js:16-51`).
- `__init__.py` — экспорт `DeggSwitch`, `WEB_DIRECTORY = "web"`.
- Git: master чистая на `eb7255c` («Simplify DeggSwitch: remove lazy 20-inputs pattern»).

## 3. Проблемы, которые встречались (и как решали)

- Входы не восстанавливаются в подграфе при загрузке → найдено, что это баг
  фронтенда ComfyUI (#12981 открыт, с official expected fix). Обходы сообщества:
  `--front-end-version Comfy-Org/ComfyUI_frontend@1.39.19`, Unpack subgraph,
  Desktop v0.8.19.
- Динамика через JS конфликтовала с механизмом подграфов → нода упрощена до
  фиксированной схемы: только `input_0`, входы добавляются lazy по мере подключения,
  но это по-прежнему не переживает вложенность в subgraph.

## 4. Что важно не сломать при продолжении работы

- НЕ менять логику селектора без теста в подграфе.
- НЕ возвращать паттерн «20 входов сразу» — он вызывал баг фронтенда.
- Изменения вносить в исходник `F:\AI_projects\Work_ComfyUI\Custom_node\Degg_Switch\`,
  затем **сразу** синк в рабочую копию (`D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\Degg_Switch\`).

## 5. Следующие шаги (идеи, не сделано)

- Если нужно работать внутри подграфов — рассмотреть альтернативную реализацию,
  не использующую динамические входы JS (например, эксепт-нода с фиксированными
  input_1…input_N).
- Дождаться фикса фронтенда (#12981) и проверить после обновления.

## 6. Связанные файлы

- `F:\AI_projects\Work_ComfyUI\Custom_node\Degg_Switch\deg_switch_node.py`
- `F:\AI_projects\Work_ComfyUI\Custom_node\Degg_Switch\web\js\deg_switch.js`
- `F:\AI_projects\Work_ComfyUI\Custom_node\Degg_Switch\__init__.py`
- `D:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\Krea2_MY2.json` — воркфлоу с подграфом «MASTER STYLE», где ломался Degg Switch