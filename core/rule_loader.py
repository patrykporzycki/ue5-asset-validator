import json

def load_rules(rules_path: str) -> dict:
    with open(rules_path, "r") as f:
        rules = json.load(f)
    return rules