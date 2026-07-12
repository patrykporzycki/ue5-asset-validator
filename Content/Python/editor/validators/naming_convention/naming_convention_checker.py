from core.types import Check
from core.types import Alert, Severity

class NamingConventionCheck(Check):
    alert_id = "naming_convention"
    severity = Severity.WARNING

    def check(self, props: dict, rules: dict) -> Alert | None:

        correct_prefix = rules['prefix_rules'].get(props['asset_class'])
        if not correct_prefix:
            return None

        if not props['name'].startswith(correct_prefix):
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Asset starts with wrong prefix, asset type suggests {correct_prefix}",
                current_value=str(props['name']),
                correct_value=None
            )
        return None

NAMING_CONVENTION_CHECKS = [
    NamingConventionCheck()
]

