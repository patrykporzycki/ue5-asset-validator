from core.types import Check


def validate(properties, rules, checks : list[Check]):
    alerts = []
    for check in checks:
        alert = check.check(properties, rules)
        if alert is not None:
            alerts.append(alert)
    return alerts