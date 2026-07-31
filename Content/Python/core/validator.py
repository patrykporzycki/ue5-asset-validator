from core.types import Check

def validate(properties, rules, checks : list[Check]):
    results = []
    for check in checks:
        alert = check.check(properties, rules)
        if alert is not None:
            results.append((alert, check))
    return results
