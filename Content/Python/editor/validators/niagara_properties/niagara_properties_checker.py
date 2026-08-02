from core.types import Check
from core.types import Alert, Severity

class UnactiveEmmitersCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        if props.emitters > props.active_emitters:
            return [Alert(
                id="unactive_emmiters",
                severity=Severity.WARNING,
                message=f"Asset has inactive emitters! Inactive emitters: {props.emitters - props.active_emitters}",
                current_value=str(props.active_emitters),
                correct_value=str(props.emitters),
            )]
        return []

NIAGARA_CHECKS = [
    UnactiveEmmitersCheck()
]
