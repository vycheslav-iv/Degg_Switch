class DeggSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "select": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 20,
                    "step": 1,
                    "tooltip": "Номер входа, который будет выведен на выход",
                }),
            },
            "optional": {},
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }
        # Объявляем все 20 входов как optional с lazy=True
        for i in range(1, 21):
            inputs["optional"][f"input_{i}"] = ("*", {"lazy": True})
        return inputs

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

    def check_lazy_status(self, select, **kwargs):
        """Запрашиваем только выбранный вход, остальные не вычисляем."""
        selected = f"input_{int(select)}"
        return [selected]

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
