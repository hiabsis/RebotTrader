import json


def to_json(data):
    return json.dumps(data, indent=4, separators=(',', ':'), ensure_ascii=False)
