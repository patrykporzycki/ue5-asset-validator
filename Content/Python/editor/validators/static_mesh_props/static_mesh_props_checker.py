from __future__ import annotations
from core.types import Check, FixOption
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
        min_tris = config.get("params", {}).get("min_triangles", 5000)

        if props.nanite != expected:
            alerts.append(Alert(
                id="nanite",
                severity=Severity.WARNING,
                message=f"Nanite is {'enabled' if props.nanite else 'disabled'}, expected {'enabled' if expected else 'disabled'}!",
                current_value=props.nanite,
                correct_value=expected,
                is_fixable=True,
            ))

        if props.nanite and props.triangles < min_tris:
            alerts.append(Alert(
                id="nanite_lowpoly",
                severity=Severity.INFO,
                message=f"Nanite enabled on a {props.triangles} triangles mesh!",
                current_value=props.triangles,
            ))

        if props.nanite and props.material_slot_blend_modes:
            for idx, mode in props.material_slot_blend_modes.items():
                if mode == "BLEND_Translucent":
                    alerts.append(Alert(
                        id="nanite_translucent",
                        severity=Severity.ERROR,
                        message=f"Nanite enabled but material slot [{idx}] uses translucent material. Nanite does not support translucent rendering!",
                        current_value=mode,
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
        params = config.get("params", {})

        if not params.get("expected_value", False):
            return []

        if props.generate_lightmap_u_vs is False and props.has_lightmap_u_vs is False:
            if props.uv_channel_count >= 8:
                return [Alert(
                    id="lightmap_no_free_channel",
                    severity=Severity.ERROR,
                    message="Mesh requires lightmaps but all 8 UV channels are in use!",
                    current_value=props.uv_channel_count,
                    is_fixable=False,
                )]
            return [Alert(
                id="generate_lightmap_u_vs",
                severity=Severity.ERROR,
                message="Mesh requires lightmaps but has no lightmap UV channel!",
                current_value=False,
                correct_value=True,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        dst_lightmap_index = props.uv_channel_count if props else 1
        src_lightmap_index = 0
        min_lightmap_resolution = 64
        if options:
            dst_lightmap_index = options.get("dst_lightmap_index", dst_lightmap_index)
            src_lightmap_index = options.get("src_lightmap_index", src_lightmap_index)
            min_lightmap_resolution = options.get("min_lightmap_resolution", 0)

        subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        for lod_index in range(subsystem.get_lod_count(asset)):
            build_settings = subsystem.get_lod_build_settings(asset, lod_index)
            build_settings.generate_lightmap_u_vs = True
            build_settings.src_lightmap_index = src_lightmap_index
            build_settings.dst_lightmap_index = dst_lightmap_index
            build_settings.min_lightmap_resolution = min_lightmap_resolution
            subsystem.set_lod_build_settings(asset, lod_index, build_settings)
        asset.set_editor_property("light_map_coordinate_index", dst_lightmap_index)
        unreal.log(f"Generated lightmap UVs into channel {dst_lightmap_index} for {asset.get_fname()}")
        return True

    def get_fix_options(self, alert, props, rules):
        dst_lightmap_index = props.uv_channel_count if props else 1
        uv_channel_count = props.uv_channel_count if props else 1
        return [
            FixOption(
                key="src_lightmap_index",
                label="Source Lightmap UV Channel",
                default=0,
                choices=tuple(range(uv_channel_count)),
            ),
            FixOption(
                key="dst_lightmap_index",
                label="Destination Lightmap UV Channel",
                default=dst_lightmap_index,
                choices=tuple(range(dst_lightmap_index, min(dst_lightmap_index + 4, 8))),
            ),
            FixOption(
                key="min_lightmap_resolution",
                label="Min Lightmap Resolution",
                default=0,
                choices=(0, 32, 64, 128, 256, 512, 1024),
            ),
        ]


SM_MESH_PROPS_CHECKS = [
    *MESH_CHECKS,
    LODsCheck(),
    CollisionsCheck(),
    NaniteCheck(),
    GenerateLightmapUVCheck(),
]
