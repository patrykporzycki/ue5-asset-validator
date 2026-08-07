from core.types import Check
from config.config_resolver import resolve_config


def validate(properties, rules, checks: list[Check]):
    results = []
    for check in checks:
        config = resolve_config(check.check_id, properties.path, rules)
        if config is None:
            continue
        alerts = check.check(properties, config)
        for alert in alerts:
            results.append((alert, check))
    return results
