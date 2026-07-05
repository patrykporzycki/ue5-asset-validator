import json

def load_rules(rules_path: str) -> dict | None:
    try:
        with open(rules_path, "r") as f:
            rules = json.load(f)
            return rules
    except FileNotFoundError:
        raise FileNotFoundError(f"File {rules_path} doesn't exist")
    except json.decoder.JSONDecodeError:
        raise ValueError(f"File {rules_path} doesn't contain valid json")