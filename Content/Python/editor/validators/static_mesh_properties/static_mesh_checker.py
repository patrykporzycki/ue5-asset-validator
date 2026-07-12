from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

class LODsCheck(Check):
    alert_id = "lods"
    severity = Severity.WARNING

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['lods'] == 1 :
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"LODs are not set!",
                current_value=str(props['lods']),
                correct_value=None
            )
        return None

class CollisionsCheck(Check):
    alert_id = "collisions"
    severity = Severity.WARNING

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['collisions'] == 0:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="Collisions are not set!",
                current_value=str(props['collisions']),
                correct_value=None
            )
        return None

STATIC_MESH_CHECKS = [
    LODsCheck(),
    CollisionsCheck()
]