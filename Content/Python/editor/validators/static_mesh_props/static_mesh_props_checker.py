from __future__ import annotations
from core.types import Check, FixOption
from core.types import Alert, Severity
from editor.validators.mesh_checks.mesh_checks import MESH_CHECKS

try:
    import unreal
except ImportError:
    unreal = None

class CollisionsCheck(Check):
    check_id = "collisions"

    def check(self, props, config) -> list[Alert]:
        alerts = []
        if props.collisions == 0:
            alerts.append(Alert(
                id="collisions",
                severity=Severity.WARNING,
                message="Collisions are not set!",
                current_value=str(props.collisions),
                correct_value=None
            ))
        min_triangles = config.get("params", {}).get("min_triangles", 100)
        if (props.collision_trace_flag
                and "CTF_USE_COMPLEX_AS_SIMPLE" in props.collision_trace_flag
                and props.triangles > min_triangles):
            alerts.append(Alert(
                id="collision_complex_as_simple",
                severity=Severity.WARNING,
                message=f"Collision uses ComplexAsSimple on a {props.triangles} triangles mesh!",
                current_value=props.collision_trace_flag,
                correct_value="CTF_USE_SIMPLE_AS_COMPLEX",
                is_fixable=False,
            ))
        return alerts

class NaniteCheck(Check):
    check_id = "nanite"
    requires_deep = True

    def is_applicable(self) -> bool:
        if unreal is None:
            return True
        return unreal.SystemLibrary.get_console_variable_bool_value("r.Nanite.ProjectEnabled")

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

        fallback_min_tris = config.get("params", {}).get("fallback_min_triangles", 10000)
        fallback_max_percent = config.get("params", {}).get("fallback_max_percent", 0.5)
        if (props.nanite
                and props.triangles >= fallback_min_tris
                and props.nanite_fallback_percent_triangles is not None
                and props.nanite_fallback_percent_triangles > fallback_max_percent):
            alerts.append(Alert(
                id="nanite_fallback_unreduced",
                severity=Severity.WARNING,
                message=f"Nanite fallback keeps {props.nanite_fallback_percent_triangles:}% of triangles on a {props.triangles} triangles mesh!",
                current_value=props.nanite_fallback_percent_triangles,
                is_fixable=True,
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
        if alert.id == "nanite_fallback_unreduced":
            fallback_percent_triangles = options.get("fallback_percent_triangles", 0.5) if options else 0.5
            nanite_settings.fallback_target = unreal.NaniteFallbackTarget.PERCENT_TRIANGLES
            nanite_settings.fallback_percent_triangles = float(fallback_percent_triangles)
            unreal.log(f"Set nanite fallback percent to {nanite_settings.fallback_percent_triangles} for {asset.get_fname()}")
        else:
            nanite_settings.enabled = alert.correct_value
            unreal.log(f"Set nanite to {alert.correct_value} for {asset.get_fname()}")
        subsystem.set_nanite_settings(asset, nanite_settings)
        return True

    def get_fix_options(self, alert, props, rules):
        if alert.id != "nanite_fallback_unreduced":
            return []
        return [
            FixOption(
                key="fallback_percent_triangles",
                label="Fallback Percent Triangles",
                default=0.5,
            ),
        ]


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
    CollisionsCheck(),
    NaniteCheck(),
    GenerateLightmapUVCheck(),
]
