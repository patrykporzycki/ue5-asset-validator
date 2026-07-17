from core.types import Check

def validate(properties, rules, checks : list[Check]):
    alerts = []
    for check in checks:
        try:
            alert = check.check(properties, rules)
            if alert is not None:
                alerts.append(alert)
        except Exception as e:
            unreal.log(f"Check {check.alert_id} failed: {e}")
            continue
    return alerts
