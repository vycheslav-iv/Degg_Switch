"""Функциональный тест DeggSwitch (Python) — без ComfyUI, без torch.

Нода — переключатель: виджет `select` выбирает, какой вход уйдёт на выход.
Тест держит места, где ошибка не видна глазом:
  • выбор по номеру (1-based) и по значению, пришедшему из сохранённого
    workflow строкой ("2") или дробью (2.9 — ComfyUI может прислать float);
  • неподключённый вход даёт None, а не исключение и не чужое значение;
  • объект проходит по ссылке (для тензоров/словарей копирование было бы
    дороже и незаметнее, чем ошибка);
  • границы 1..20 совпадают с обещанием в DESCRIPTION (входы до 20-го).

Запуск:  cd Degg_Switch && python tests/_test_deg_switch.py
"""

import importlib.util
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parent.parent / "deg_switch_node.py"

fails = []
oks = []


def _p(text):
    try:
        enc = sys.stdout.encoding or "utf-8"
        sys.stdout.write(str(text).encode(enc, "replace").decode(enc, "replace") + "\n")
    except Exception:
        pass


def check(name, cond, extra=""):
    (oks if cond else fails).append(name)
    _p(("  ok  " if cond else "  FAIL") + f"  {name}" + (f"  [{extra}]" if extra and not cond else ""))


spec = importlib.util.spec_from_file_location("deg_switch_node", NODE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

Cls = mod.NODE_CLASS_MAPPINGS["DeggSwitch"]
it = Cls.INPUT_TYPES()
node = Cls()

# ────────────────────────────── контракт входа ──────────────────────────────
sel = it["required"]["select"]
check("INPUT_TYPES: select — INT с границами 1..20",
      sel[0] == "INT" and sel[1].get("min") == 1 and sel[1].get("max") == 20, sel)
check("INPUT_TYPES: select default = 1 и step = 1",
      sel[1].get("default") == 1 and sel[1].get("step") == 1, sel[1])
check("INPUT_TYPES: первый вход — optional input_1",
      list(it.get("optional", {})) == ["input_1"], list(it.get("optional", {})))
check("INPUT_TYPES: вход принимает любой тип (*)", it["optional"]["input_1"][0] == "*",
      it["optional"]["input_1"])

# ──────────────────────────────── выбор входа ───────────────────────────────
check("process(1): берёт input_1", node.process(1, input_1="a", input_2="b") == ("a",),
      node.process(1, input_1="a", input_2="b"))
check("process(2): берёт input_2", node.process(2, input_1="a", input_2="b") == ("b",),
      node.process(2, input_1="a", input_2="b"))
check("process(20): последний вход из обещанных 20 работает",
      node.process(20, input_1="a", input_20="z") == ("z",),
      node.process(20, input_1="a", input_20="z"))
check("process: строка из workflow (\"2\") выбирает тот же вход",
      node.process("2", input_1="a", input_2="b") == ("b",),
      node.process("2", input_1="a", input_2="b"))
check("process: дробное 2.9 не уводит выбор на 3-й вход (int(), а не round)",
      node.process(2.9, input_2="b", input_3="c") == ("b",),
      node.process(2.9, input_2="b", input_3="c"))
check("process: неподключённый вход даёт None, а не исключение",
      node.process(3, input_1="a") == (None,), node.process(3, input_1="a"))
check("process: явный None в выбранном входе остаётся None",
      node.process(1, input_1=None, input_2="b") == (None,))
check("process: чужие ключи не подменяют выбор",
      node.process(1, input_1="a", input_99="чужое") == ("a",))

obj = {"tensor": [1, 2, 3]}
out = node.process(1, input_1=obj)
check("process: объект проходит по ссылке, без копирования", out[0] is obj, type(out[0]))

# ─────────────────────────── метаданные класса/меню ────────────────────────
check("RETURN_TYPES = (*,)", Cls.RETURN_TYPES == ("*",), Cls.RETURN_TYPES)
check("RETURN_NAMES = (output,)", Cls.RETURN_NAMES == ("output",), Cls.RETURN_NAMES)
check("FUNCTION = process", Cls.FUNCTION == "process", Cls.FUNCTION)
check("REGISTRY-ключ не переименован", mod.NODE_CLASS_MAPPINGS == {"DeggSwitch": Cls},
      list(mod.NODE_CLASS_MAPPINGS))
check("имя в меню на месте",
      mod.NODE_DISPLAY_NAME_MAPPINGS.get("DeggSwitch") == "Degg Switch",
      mod.NODE_DISPLAY_NAME_MAPPINGS)

_p("")
_p(f"PASS: {len(oks)}  FAIL: {len(fails)}")
if fails:
    _p("failed: " + ", ".join(fails))
else:
    _p("ТЕСТ ПРОЙДЕН")
sys.exit(1 if fails else 0)
