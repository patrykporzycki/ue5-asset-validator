from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

try:
    import unreal
except ImportError:
    unreal = None

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

class BoneInfluencesCheck(Check):
    alert_id = "bone_influences"
    severity = Severity.WARNING
    is_fixable = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['max_bone_influences'] > rules['max_bone_influences'] :
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Max bone influence is bigger than {rules['max_bone_influences']}!",
                current_value=str(props['max_bone_influences']),
                correct_value=rules['max_bone_influences']
            )
        return None

    def fix(self, asset, alert):
        SkinWeightModifier = unreal.SkinWeightModifier()
        if not SkinWeightModifier.set_skeletal_mesh(asset):
            raise RuntimeError(f"Failed to load skeletal mesh for weight editing")
        SkinWeightModifier.enforce_max_influences(alert.correct_value)
        SkinWeightModifier.commit_weights_to_skeletal_mesh()
        unreal.log(f"Fixed bone influences for asset {asset.get_fname()}. Reduced from {alert.current_value} to {alert.correct_value}")

        return True

SKELETAL_MESH_CHECKS = [
    LODsCheck(),
    BoneInfluencesCheck()
]