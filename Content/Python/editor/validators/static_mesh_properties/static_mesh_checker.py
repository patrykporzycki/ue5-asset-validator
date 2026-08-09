from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity
from editor.validators.mesh_checks.mesh_checks import MESH_CHECKS

try:
    import unreal
except ImportError:
    unreal = None


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

class NaniteCheck(Check):
    check_id = "nanite"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        alerts = []
        expected = config.get("params", {}).get("expected_value", True)
        min_tri = config.get("params", {}).get("min_triangles", 5000)

        if props.nanite != expected:
            alerts.append(Alert(
                id="nanite",
                severity=Severity.WARNING,
                message=f"Nanite is {'enabled' if props.nanite else 'disabled'}, expected {'enabled' if expected else 'disabled'}!",
                current_value=props.nanite,
                correct_value=expected,
                is_fixable=True,
            ))

        if props.nanite and props.triangles < min_tri:
            alerts.append(Alert(
                id="nanite_lowpoly",
                severity=Severity.INFO,
                message=f"Nanite enabled on a {props.triangles} triangles mesh!",
                current_value=props.triangles,
            ))

        return alerts

    def fix(self, asset, alert, props=None, options=None):
        if alert.id == "nanite_lowpoly":
            return False
        subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        nanite_settings = subsystem.get_nanite_settings(asset)
        nanite_settings.enabled = alert.correct_value
        subsystem.set_nanite_settings(asset, nanite_settings)
        unreal.log(f"Set nanite to {alert.correct_value} for {asset.get_fname()}")
        return True


class GenerateLightmapUVCheck(Check):
    check_id = "generate_lightmap_u_vs"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        if props.generate_lightmap_u_vs is False:
            return [Alert(
                id="generate_lightmap_u_vs",
                severity=Severity.WARNING,
                message="Generate Lightmap UVs is OFF, no lightmap UV channel for static lighting!",
                current_value=False,
                correct_value=True,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        for i in range(subsystem.get_lod_count(asset)):
            build_settings = subsystem.get_lod_build_settings(asset, i)
            build_settings.generate_lightmap_u_vs = True
            subsystem.set_lod_build_settings(asset, i, build_settings)
        unreal.log(f"Set generate_lightmap_u_vs true for {asset.get_fname()}")
        return True


SM_MESH_PROPERTIES_CHECKS = [
    *MESH_CHECKS,
    LODsCheck(),
    CollisionsCheck(),
    NaniteCheck(),
    GenerateLightmapUVCheck(),
]
