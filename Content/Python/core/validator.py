from core.types import Check

def validate(properties, rules, checks : list[Check]):
    alerts = []
    for check in checks:
        try:
            alert = check.check(properties, rules)
            if alert is not None:
                alerts.append(alert)
        except Exception:
            continue
    return alerts
