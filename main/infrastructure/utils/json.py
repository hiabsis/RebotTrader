import json


class JsonUtil:
    @staticmethod
    def object2json(ojt):
        return json.dumps(ojt, default=lambda obj: obj.__dict__, sort_keys=False, ensure_ascii=False, indent=3)

    @staticmethod
    def read_as_dict(file):
        with open(file) as f:
            return json.load(f)
