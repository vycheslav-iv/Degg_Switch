class DeggSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "select": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 20,
                    "step": 1,
                    "tooltip": "Номер входа, который будет выведен на выход",
                }),
            },
            "optional": {
                "input_1": ("*", {}),
            },
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("output",)
    FUNCTION = "process"
    CATEGORY = "My_custom_nodes"
    DESCRIPTION = (
        "Переключатель входов. "
        "Подключите несколько источников данных и выберите через select, "
        "какой из них передать на выход.\n"
        "Входы создаются динамически — при подключении к входу N появляется вход N+1. "
        "Максимум 20 входов."
    )

    def process(self, select, **kwargs):
        selected = f"input_{int(select)}"
        value = kwargs.get(selected)
        return (value,)


NODE_CLASS_MAPPINGS = {
    "DeggSwitch": DeggSwitch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DeggSwitch": "Degg Switch",
}
