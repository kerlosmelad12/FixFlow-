import os
class Templete_parser:

    def __init__(self, lang: str, default_lang: str = "en"):
        self.default_lang = default_lang
        self.current_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.lang = self.set_languadge(lang=lang)

    def set_languadge(self, lang: str):
        if lang is None:
            self.lang = self.default_lang
            return self.lang

        lang_path = os.path.join(self.current_dir_path, "locales", lang)
        if os.path.exists(lang_path):
            self.lang = lang
        else:
            self.lang = self.default_lang
        return self.lang

    def get(self, group: str, key: str, variables: dict = None):
        if group is None or key is None:
            return None

        variables = variables or {}

        target_lang = self.lang
        group_path = os.path.join(self.current_dir_path, "locales", target_lang, f"{group}.py")
        if not os.path.exists(group_path):
            target_lang = self.default_lang

        module = __import__(f"templetes.locales.{target_lang}.{group}", fromlist=[group])

        if module is None:
            return None

        key_attribute = getattr(module, key, None)
        if key_attribute is None:
            return None

        return key_attribute.substitute(variables)