from core.types import Check
from core.types import Alert, Severity


class NamingConventionCheck(Check):
    check_id = "naming_convention"

    def check(self, props, config) -> list[Alert]:
        correct_prefix = config["params"]["prefix_rules"].get(props.asset_class)
        if correct_prefix is None:
            return []
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
