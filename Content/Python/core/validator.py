from core.texture_checker import TEXTURE_CHECKS

def validate(properties, rules):
    alerts = []
    for check_name, check_fn in TEXTURE_CHECKS.items():
        alert = check_fn(properties, rules)
        if alert is not None:
            alerts.append(alert)
    return alerts