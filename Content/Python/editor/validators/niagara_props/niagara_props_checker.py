from core.types import Check
from core.types import Alert, Severity


class InactiveEmittersCheck(Check):
    check_id = "inactive_emitters"

    def check(self, props, config) -> list[Alert]:
        if props.emitters > props.active_emitters:
            return [Alert(
                id="inactive_emitters",
                severity=Severity.WARNING,
                message=f"Asset has inactive emitters! Inactive emitters: {props.emitters - props.active_emitters}",
                current_value=str(props.active_emitters),
                correct_value=str(props.emitters),
            )]
        return []


NIAGARA_CHECKS = [
    InactiveEmittersCheck()
]
