from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

try:
    import unreal
except ImportError:
    unreal = None

class BrokenReferencesCheck(Check):
    alert_id = "broken_references"
    severity = Severity.ERROR

    def check(self, props: dict, rules: dict) -> Alert | None:

        if props['broken_references']:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Detected {len(props['broken_references'])} broken references: " + ", ".join(props['broken_references']),
                current_value=str(len(props['broken_references'])),
                correct_value=0
            )
        return None

BROKEN_REFERENCES_CHECKS = [
    BrokenReferencesCheck()
]