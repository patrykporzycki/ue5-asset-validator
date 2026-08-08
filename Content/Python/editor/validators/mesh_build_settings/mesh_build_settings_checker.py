from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

try:
    import unreal
except ImportError:
    unreal = None

def _fix_build_setting(asset, property_name, value):
    if isinstance(asset, unreal.StaticMesh):
        subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    else:
        subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    for i in range(subsystem.get_lod_count(asset)):
        build_settings = subsystem.get_lod_build_settings(asset, i)
        build_settings.set_editor_property(property_name, value)
        subsystem.set_lod_build_settings(asset, i, build_settings)

class MikkTSpaceCheck(Check):
    check_id = "mikk_t_space"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        if props.mikk_t_space is False:
            return [Alert(
                id="mikk_t_space",
                severity=Severity.ERROR,
                message="MikkTSpace is disabled, normal maps will look broken in other DCC tools.",
                current_value=str(props.mikk_t_space),
                correct_value=True,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        _fix_build_setting(asset, "use_mikk_t_space", alert.correct_value)
        unreal.log(f"Set use_mikk_t_space true for {asset.get_fname()}")
        return True

class NoTangentSourceCheck(Check):
    check_id = "no_tangent_source"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        if props.recompute_tangents is False and props.mikk_t_space is False:
            return [Alert(
                id="no_tangent_source",
                severity=Severity.ERROR,
                message="No tangent source: both Recompute Tangents and MikkTSpace are off. Mesh has no valid tangents for normal maps.",
                current_value={"recompute_tangents": False, "mikk_t_space": False},
                correct_value={"mikk_t_space": True},
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        _fix_build_setting(asset, "use_mikk_t_space", True)
        unreal.log(f"Fixed tangent basis for {asset.get_fname()}")
        return True

class RecomputeNormalsCheck(Check):
    check_id = "recompute_normals"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        expected = config.get("params", {}).get("expected_value", False)
        if props.recompute_normals is None:
            return []
        if props.recompute_normals != expected:
            return [Alert(
                id="recompute_normals",
                severity=Severity.WARNING,
                message="Recompute Normals is ON, discarding DCC normals." if props.recompute_normals else "Recompute Normals is OFF.",
                current_value=str(props.recompute_normals),
                correct_value=expected,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        _fix_build_setting(asset, "recompute_normals", alert.correct_value)
        unreal.log(f"Set recompute_normals to {alert.correct_value} for {asset.get_fname()}")
        return True

class RecomputeTangentsCheck(Check):
    check_id = "recompute_tangents"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        expected = config.get("params", {}).get("expected_value", False)
        if props.recompute_tangents is None:
            return []
        if props.recompute_tangents != expected:
            return [Alert(
                id="recompute_tangents",
                severity=Severity.WARNING,
                message="Recompute Tangents is ON." if props.recompute_tangents else "Recompute Tangents is OFF.",
                current_value=str(props.recompute_tangents),
                correct_value=expected,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        _fix_build_setting(asset, "recompute_tangents", alert.correct_value)
        unreal.log(f"Set recompute_tangents to {alert.correct_value} for {asset.get_fname()}")
        return True

class RemoveDegeneratesCheck(Check):
    check_id = "remove_degenerates"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        if props.remove_degenerates is False:
            return [Alert(
                id="remove_degenerates",
                severity=Severity.WARNING,
                message="Remove Degenerates is OFF.",
                current_value=False,
                correct_value=True,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        _fix_build_setting(asset, "remove_degenerates", True)
        unreal.log(f"Set remove_degenerates true for {asset.get_fname()}")
        return True


MESH_BUILD_SETTINGS_CHECKS = [
    MikkTSpaceCheck(),
    NoTangentSourceCheck(),
    RecomputeNormalsCheck(),
    RecomputeTangentsCheck(),
    RemoveDegeneratesCheck(),
]
