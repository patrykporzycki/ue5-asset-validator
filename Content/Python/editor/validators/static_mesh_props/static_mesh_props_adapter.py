from dataclasses import dataclass
from core.types import AssetAdapter, BaseProps

import unreal


def _get_mikk_t_space(asset) -> bool:
    subsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for lod in range(subsys.get_lod_count(asset)):
        build_settings = subsys.get_lod_build_settings(asset, lod)
        if not build_settings.get_editor_property("use_mikk_t_space"):
            return False
    return True

def _get_build_settings(asset, build_property):
    subsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for lod in range(subsys.get_lod_count(asset)):
        build_settings = subsys.get_lod_build_settings(asset, lod)
        if build_settings.get_editor_property(build_property):
            return True
    return False

def _has_degenerates_triangles(asset):
    return unreal.MeshPropsHelper.static_mesh_has_degenerate_triangles(asset)

def _get_material_slot_blend_modes(asset):
    modes = {}
    for i, static_mat in enumerate(asset.static_materials):
        material_interface = static_mat.material_interface
        if material_interface:
            modes[i] = str(material_interface.get_blend_mode())
    return modes

@dataclass
class StaticMeshProps(BaseProps):
    triangles: int = 0
    materials: int = 0
    lods: int = 0
    collisions: int = 0
    nanite: bool = False

    recompute_normals: bool | None = None
    recompute_tangents: bool | None = None
    mikk_t_space: bool | None = None
    generate_lightmap_u_vs: bool | None = None
    remove_degenerates: bool | None = None
    has_degenerates_triangles: bool | None = None
    material_slot_blend_modes: dict[int, str] | None = None

class StaticMeshPropsAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        props = StaticMeshProps(
            name=str(asset_data.asset_name),
            path=str(asset_data.package_name),
            triangles=int(self.get_tag(asset_data, "Triangles") or 0),
            materials=int(self.get_tag(asset_data, "Materials") or 0),
            lods=int(self.get_tag(asset_data, "LODs") or 0),
            collisions=int(self.get_tag(asset_data, "CollisionPrims") or 0),
            nanite=bool(self.get_tag(asset_data, "NaniteEnabled") or 0),
        )
        if asset:
            props.recompute_normals = _get_build_settings(asset, "recompute_normals")
            props.recompute_tangents = _get_build_settings(asset, "recompute_tangents")
            props.mikk_t_space = _get_mikk_t_space(asset)
            props.generate_lightmap_u_vs = _get_build_settings(asset, "generate_lightmap_u_vs")
            props.remove_degenerates = _get_build_settings(asset, "remove_degenerates")
            props.has_degenerates_triangles = _has_degenerates_triangles(asset)
            props.material_slot_blend_modes = _get_material_slot_blend_modes(asset)
        return props
