from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity, FixOption
from editor.validators.skeletal_mesh_props.skeletal_mesh_props_adapter import SkeletalMeshProps

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
                message="MikkTSpace is disabled, normal maps will look broken!",
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
                message="No tangent source: both Recompute Tangents and MikkTSpace are off. Mesh has no valid tangents for normal maps!",
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
                message="Recompute Normals is ON, discarding source normals." if props.recompute_normals else "Recompute Normals is OFF.",
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
                message="Recompute Tangents is OFF but mesh has morph targets, it must be ON!" if props.has_morph_targets else "Recompute Tangents is ON." if props.recompute_tangents else "Recompute Tangents is OFF.",
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
        if props.has_degenerates_triangles is True and props.remove_degenerates is False:
            return [Alert(
                id="remove_degenerates",
                severity=Severity.WARNING,
                message="Mesh has degenerate triangles but Remove Degenerates is OFF!",
                current_value=False,
                correct_value=True,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        _fix_build_setting(asset, "remove_degenerates", True)
        unreal.log(f"Set remove_degenerates true for {asset.get_fname()}")
        return True

class TriangleCountCheck(Check):
    check_id = "triangle_count"

    def check(self, props, config) -> list[Alert]:
        max_tris_count = config.get("params", {}).get("max_triangles", 0)
        if max_tris_count and props.triangles > max_tris_count:
            return [Alert(
                id="triangle_count",
                severity=Severity.WARNING,
                message=f"{props.triangles} triangles exceeds limit of {max_tris_count}!",
                current_value=props.triangles,
                correct_value=max_tris_count,
            )]
        return []

class UnusedMaterialSlotsCheck(Check):
    check_id = "unused_material_slots"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        unused = [
            material for index, material in enumerate(props.materials)
            if index not in props.slot_section_usage
        ]
        if not unused:
            return []
        return [Alert(
            id="unused_material_slots",
            severity=Severity.WARNING,
            message=f"Unused materials slots: {len(unused)}!",
            current_value=str(len(unused)),
            is_fixable=True,
        )]

    def fix(self, asset, alert, props=None, options=None):
        if isinstance(asset, unreal.StaticMesh):
            materials = asset.get_editor_property("static_materials")
            used_indices = set(props.slot_section_usage.keys())
            new_materials = [material for index, material in enumerate(materials) if index in used_indices]
            asset.set_editor_property("static_materials", new_materials)
        else:
            materials = asset.get_editor_property("materials")
            used_indices = set(props.slot_section_usage.keys())
            new_materials = [material for index, material in enumerate(materials) if index in used_indices]
            asset.set_editor_property("materials", new_materials)
        unreal.log(f"Removed {len(materials) - len(new_materials)} unused material slots from {asset.get_fname()}")
        return True

def _is_skeletal_mesh(props, asset=None):
    if props is not None:
        return isinstance(props, SkeletalMeshProps)
    return isinstance(asset, unreal.SkeletalMesh)


def _default_lod_reduction(lod):
    return {
        "percent_triangles": 1.0 if lod == 0 else 0.5 ** lod,
        "screen_size": 1.0 if lod == 0 else 0.5 ** lod,
    }


def _reduction_settings_presets(rules):
    presets = []
    for preset in rules.get("presets", []):
        if preset.get("reduction_settings"):
            presets.append(preset)
    return presets


def _collect_lod_reduction_settings(options, num_lods):
    settings = []
    for lod in range(num_lods):
        percent_triangles = options.get(f"lod_{lod}_percent_triangles")
        screen_size = options.get(f"lod_{lod}_screen_size")
        if percent_triangles is None and screen_size is None:
            settings.append({})
        else:
            settings.append({
                "percent_triangles": float(percent_triangles),
                "screen_size": float(screen_size),
            })
    return settings


def _static_mesh_reduction_options(num_lods, auto_compute_lod_screen_size, reduction_settings):
    options = unreal.StaticMeshReductionOptions()
    options.auto_compute_lod_screen_size = auto_compute_lod_screen_size
    settings = []
    for lod in range(num_lods):
        reduction = unreal.StaticMeshReductionSettings()
        default = _default_lod_reduction(lod)
        lod_settings = reduction_settings[lod] if lod < len(reduction_settings) else {}
        reduction.percent_triangles = lod_settings.get("percent_triangles", default["percent_triangles"])
        reduction.screen_size = lod_settings.get("screen_size", default["screen_size"])
        settings.append(reduction)
    options.reduction_settings = settings
    return options


class LODsCheck(Check):
    check_id = "lods"

    def check(self, props, config) -> list[Alert]:
        params = config.get("params", {})
        min_lods = params.get("min_lods", 2)
        if props.lods >= min_lods:
            return []
        return [Alert(
            id="lods",
            severity=Severity.WARNING,
            message="LODs are not set!",
            current_value=str(props.lods),
            correct_value=params.get("num_lods", 3),
            is_fixable=True,
        )]

    def fix(self, asset, alert, props=None, options=None):
        options = options or {}
        num_lods = int(options.get("num_lods", alert.correct_value))

        if _is_skeletal_mesh(props, asset):
            subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
            subsystem.regenerate_lod(asset, num_lods, True, False)
            if "lod_settings" in options:
                asset.set_editor_property("lod_settings", options["lod_settings"])
        else:
            subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
            if options.get("lod_group"):
                subsystem.set_lod_group(asset, options["lod_group"])
            auto_compute_lod_screen_size = options.get("auto_compute_lod_screen_size", True)
            reduction_settings = _collect_lod_reduction_settings(options, num_lods)
            reduction_options = _static_mesh_reduction_options(num_lods, auto_compute_lod_screen_size, reduction_settings)
            subsystem.set_lods(asset, reduction_options)

        unreal.log(f"Set LODs to {num_lods} for {asset.get_fname()}")
        return True

    def get_fix_options(self, alert, props, rules):
        num_lods = int(alert.correct_value)
        presets = _reduction_settings_presets(rules)
        active_preset = presets[0] if presets else None
        active_reduction_settings = active_preset.get("reduction_settings", []) if active_preset else []

        options = [FixOption(
            key="num_lods",
            label="Number of LODs",
            default=num_lods,
            choices=tuple(range(1, 9)),
        )]
        if _is_skeletal_mesh(props):
            options.append(FixOption(
                key="lod_settings",
                label="LOD Settings",
                default=None,
            ))
            return options

        options.append(FixOption(
            key="lod_group",
            label="LOD Group",
            default="",
        ))
        options.append(FixOption(
            key="auto_compute_lod_screen_size",
            label="Auto Compute LOD Screen Size",
            default=True,
            choices=(True, False),
        ))
        if presets:
            options.append(FixOption(
                key="reduction_settings_preset",
                label="Reduction Settings Preset",
                default=active_preset["name"],
                choices=tuple(preset["name"] for preset in presets),
            ))
        for lod in range(num_lods):
            preset_lod = active_reduction_settings[lod] if lod < len(active_reduction_settings) else {}
            default = _default_lod_reduction(lod)
            options.append(FixOption(
                key=f"lod_{lod}_percent_triangles",
                label=f"LOD {lod} Percent Triangles",
                default=float(preset_lod.get("percent_triangles", default["percent_triangles"])),
            ))
            options.append(FixOption(
                key=f"lod_{lod}_screen_size",
                label=f"LOD {lod} Screen Size",
                default=float(preset_lod.get("screen_size", default["screen_size"])),
            ))
        return options


MESH_CHECKS = [
    MikkTSpaceCheck(),
    NoTangentSourceCheck(),
    RecomputeNormalsCheck(),
    RecomputeTangentsCheck(),
    RemoveDegeneratesCheck(),
    TriangleCountCheck(),
    UnusedMaterialSlotsCheck(),
    LODsCheck(),
]
