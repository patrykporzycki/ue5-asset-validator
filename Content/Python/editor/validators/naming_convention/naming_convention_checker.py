from core.types import Check
from core.types import Alert, Severity

class NamingConventionCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        correct_prefix = rules['prefix_rules'].get(props.asset_class)

        if not props.name.startswith(correct_prefix):
            return [Alert(
                id="naming_convention",
                severity=Severity.WARNING,
                message=f"Asset starts with wrong prefix, asset type suggests {correct_prefix}",
                current_value=str(props.name),
            )]
        return []

NAMING_CONVENTION_CHECKS = [
    NamingConventionCheck()
]
