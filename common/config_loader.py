import json
import pathlib


class ConfigLoader:
    @staticmethod
    def load():
        script_path = pathlib.Path(__file__).parent.absolute()
        with open(f"{script_path}/../configs/config.json") as json_file:
            return json.load(json_file)

    @staticmethod
    def load_email_template(template_name):
        script_path = pathlib.Path(__file__).parent.absolute()
        with open(f"{script_path}/../configs/{template_name}.html", encoding="utf-8") as file:
            return file.read()
