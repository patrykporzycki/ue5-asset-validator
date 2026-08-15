from dataclasses import dataclass
from core.types import AssetAdapter, BaseProps

import unreal
from editor.validators.mesh_checks.mesh_utils import get_build_setting, get_mikk_t_space, get_materials_properties


def _has_degenerates_triangles(asset):
    return unreal.MeshPropsHelper.static_mesh_has_degenerate_triangles(asset)

def _has_lightmap_u_vs(asset):
    return unreal.MeshPropsHelper.static_mesh_has_lightmap_u_vs(asset)

def _get_uv_channel_count(asset):
    return unreal.MeshPropsHelper.static_mesh_get_uv_channel_count(asset)

def _get_material_slot_blend_modes(asset):
    modes = {}
    for i, static_mat in enumerate(asset.static_materials):
        material_interface = static_mat.material_interface
        if material_interface:
            modes[i] = str(material_interface.get_blend_mode())
    return modes

def _get_nanite_settings(asset):
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    return subsystem.get_nanite_settings(asset)

def _get_collision_trace_flag(asset):
    body_setup = asset.get_editor_property("body_setup")
    if body_setup is None:
        return None
    return str(body_setup.get_editor_property("collision_trace_flag"))

@dataclass
class StaticMeshProps(BaseProps):
    triangles: int = 0
    material_count: int = 0
    lods: int = 0
    collisions: int = 0
    nanite: bool = False

    recompute_normals: bool | None = None
    recompute_tangents: bool | None = None
    mikk_t_space: bool | None = None
    generate_lightmap_u_vs: bool | None = None
    remove_degenerates: bool | None = None
    has_degenerates_triangles: bool | None = None
    has_lightmap_u_vs: bool | None = None
    uv_channel_count: int = 0
    material_slot_blend_modes: dict[int, str] | None = None
    materials: list | None = None
    slot_section_usage: dict[int, set[int]] | None = None
    collision_trace_flag: str | None = None
    nanite_fallback_percent_triangles: float | None = None

class StaticMeshPropsAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        props = StaticMeshProps(
            name=str(asset_data.asset_name),
            path=str(asset_data.package_name),
            triangles=int(self.get_tag(asset_data, "Triangles") or 0),
            material_count=int(self.get_tag(asset_data, "Materials") or 0),
            lods=int(self.get_tag(asset_data, "LODs") or 0),
            collisions=int(self.get_tag(asset_data, "CollisionPrims") or 0),
        )
        if asset:
            nanite_settings = _get_nanite_settings(asset)
            props.nanite = nanite_settings.enabled
            props.nanite_fallback_percent_triangles = nanite_settings.fallback_percent_triangles
            props.recompute_normals = get_build_setting(asset, "recompute_normals")
            props.recompute_tangents = get_build_setting(asset, "recompute_tangents")
            props.mikk_t_space = get_mikk_t_space(asset)
            props.collision_trace_flag = _get_collision_trace_flag(asset)
            props.generate_lightmap_u_vs = get_build_setting(asset, "generate_lightmap_u_vs")
            props.remove_degenerates = get_build_setting(asset, "remove_degenerates")
            props.has_degenerates_triangles = _has_degenerates_triangles(asset)
            props.has_lightmap_u_vs = _has_lightmap_u_vs(asset)
            props.uv_channel_count = _get_uv_channel_count(asset)
            props.material_slot_blend_modes = _get_material_slot_blend_modes(asset)
            props.materials, props.slot_section_usage = get_materials_properties(asset)
        return props
