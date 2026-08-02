from core.types import Check

def validate(properties, rules, checks : list[Check]):
    results = []
    for check in checks:
        alerts = check.check(properties, rules)
        for alert in alerts:
            results.append((alert, check))
    return results
