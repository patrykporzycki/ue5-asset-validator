from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

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


class UnusedAssetCheck(Check):
    alert_id = "unused_asset"
    severity = Severity.WARNING

    def check(self, props: dict, rules: dict) -> Alert | None:

        if not props['referencers']:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="Asset is not referenced by any other asset!",
                current_value=str(len(props['referencers'])),
                correct_value=None
            )
        return None


REFERENCES_CHECKS = [
    BrokenReferencesCheck(),
    UnusedAssetCheck()
]