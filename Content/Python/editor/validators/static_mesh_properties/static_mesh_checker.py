from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity


class LODsCheck(Check):
    check_id = "lods"

    def check(self, props, config) -> list[Alert]:
        if props.lods == 1:
            return [Alert(
                id="lods",
                severity=Severity.WARNING,
                message="LODs are not set!",
                current_value=str(props.lods),
            )]
        return []


class CollisionsCheck(Check):
    check_id = "collisions"

    def check(self, props, config) -> list[Alert]:
        if props.collisions == 0:
            return [Alert(
                id="collisions",
                severity=Severity.WARNING,
                message="Collisions are not set!",
                current_value=str(props.collisions),
                correct_value=None
            )]
        return []


SM_MESH_PROPERTIES_CHECKS = [
    LODsCheck(),
    CollisionsCheck()
]
