from core.types import Check

def validate(properties, rules, checks : list[Check], deep=False):
    alerts = []
    for check in checks:
        if check.requires_deep and not deep:
            continue
        alert = check.check(properties, rules)
        if alert is not None:
            alerts.append(alert)
    return alerts
