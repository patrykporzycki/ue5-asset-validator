from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

class BrokenReferencesCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        if props.broken_references:
            return [Alert(
                id="broken_references",
                severity=Severity.ERROR,
                message=f"Detected {len(props.broken_references)} broken references: " + ", ".join(props.broken_references),
                current_value=str(len(props.broken_references)),
                correct_value=0
            )]
        return []


class UnusedAssetCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        if not props.referencers:
            return [Alert(
                id="unused_asset",
                severity=Severity.WARNING,
                message="Asset is not referenced by any other asset!",
                current_value=str(len(props.referencers)),
            )]
        return []


REFERENCES_CHECKS = [
    BrokenReferencesCheck(),
    UnusedAssetCheck()
]
