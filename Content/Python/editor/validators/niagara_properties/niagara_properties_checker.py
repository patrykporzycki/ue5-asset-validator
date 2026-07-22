from core.types import Check
from core.types import Alert, Severity

class UnactiveEmmitersCheck(Check):
    alert_id = "unactive_emmiters"
    severity = Severity.WARNING

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['emitters'] > props['active_emitters'] :
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Asset has unactive emitters! Unactive emitters: {props['emitters'] - props['active_emitters']}",
                current_value=str(props['active_emitters']),
                correct_value=str(props['emitters']),
            )
        return None

NIAGARA_CHECKS = [
    UnactiveEmmitersCheck()
]