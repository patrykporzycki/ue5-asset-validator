from dataclasses import dataclass

import unreal
from core.types import AssetAdapter, BaseProps

def _get_materials_properties(asset):
    slot_section_usage = {}
    SkeletalMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    for lod in range(SkeletalMeshEditorSubsystem.get_lod_count(asset)):
        for section in range(SkeletalMeshEditorSubsystem.get_num_sections(asset, lod)):
            slot_index = SkeletalMeshEditorSubsystem.get_lod_material_slot(asset, lod, section)
            if slot_index >= 0:
                if slot_index not in slot_section_usage:
                    slot_section_usage[slot_index] = set()
                slot_section_usage[slot_index].add(section)

    materials = asset.get_editor_property("materials")
    material_slots = []
    for material in materials:
        material_interface = material.get_editor_property("material_interface")
        material_slots.append({
            "slot_name": material.get_editor_property("material_slot_name"),
            "material": material_interface.get_name() if material_interface else None,
        })

    return material_slots, slot_section_usage

def _get_mikk_t_space(asset) -> bool:
    for model in asset.get_editor_property("source_models"):
        build_settings = model.get_editor_property("build_settings")
        if not build_settings.get_editor_property("use_mikk_t_space"):
            return False
    return True

def _get_build_settings(asset, build_property):
    for model in (asset.get_editor_property("source_models")):
        build_settings = model.get_editor_property("build_settings")
        if build_settings.get_editor_property(build_property):
            return True
    return False

def _get_clothing_asset_count(asset):
    clothing_asset_count = len(asset.get_editor_property("mesh_clothing_assets"))
    return clothing_asset_count


def _has_tangents_vertex_mask_channel(asset) -> bool:
    subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    for lod in range(subsystem.get_lod_count(asset)):
        for section in range(subsystem.get_num_sections(asset, lod)):
            mask = subsystem.get_section_recompute_tangents_vertex_mask_channel(asset, lod, section)
            if mask is not None and int(mask) < 3:
                return True
    return False

def _get_mesh_bones_hierarchy(asset) -> dict[str, str | None]:
    modifier = unreal.SkeletonModifier()
    if not modifier.set_skeletal_mesh(asset):
        return {}
    parents = {}
    for bone in modifier.get_all_bone_names():
        bone_str = str(bone)
        parent = modifier.get_parent_name(bone_str)
        parents[bone_str] = str(parent) if parent and str(parent) != "None" else None
    return parents

def _get_reference_bones_hierarchy(asset) -> dict[str, str | None]:
    bone_names = [bone for bone in unreal.SkeletalMeshPropsHelper.get_skeleton_bone_names(asset)]
    parent_indices = list(unreal.SkeletalMeshPropsHelper.get_reference_skeleton_indices(asset))

    parents = {}
    for i, name in enumerate(bone_names):
        index = parent_indices[i]
        parents[name] = bone_names[index] if index >= 0 else None
    return parents

def _has_degenerates_triangles(asset):
    return unreal.MeshPropsHelper.skeletal_mesh_has_degenerate_triangles(asset)

@dataclass
class SkeletalMeshProps(BaseProps):
    triangles: int = 0
    lods: int = 0
    bones: int = 0
    max_bone_influences: int = 0
    skeleton: str = ""
    physics_asset: str = ""
    morphs: int = 0

    clothing_assets_count: int | None = None
    has_degenerates_triangles: bool | None = None
    recompute_normals: bool | None = None
    recompute_tangents: bool | None = None
    mikk_t_space: bool | None = None
    remove_degenerates: bool | None = None
    has_tangents_vertex_mask: bool | None = None
    materials: list | None = None
    slot_section_usage: dict[int, set[int]] | None = None
    mesh_bones_hierarchy: dict[str, str | None] | None = None
    reference_bones_hierarchy: dict[str, str | None] | None = None


class SkeletalMeshPropsAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None) -> SkeletalMeshProps:
        props = SkeletalMeshProps(
            name = str(asset_data.asset_name),
            path=str(asset_data.package_name),
            triangles = int(self.get_tag(asset_data, "Triangles") or 0),
            lods = int(self.get_tag(asset_data, "LODs") or 0),
            bones =  int(self.get_tag(asset_data, "Bones") or 0),
            max_bone_influences = int(self.get_tag(asset_data, "MaxBoneInfluences") or 0),
            skeleton = str(self.get_tag(asset_data, "Skeleton")),
            physics_asset = str(self.get_tag(asset_data, "PhysicsAsset")),
            morphs = int(self.get_tag(asset_data, "MorphTargets") or 0),
        )
        if asset:
            props.clothing_assets_count = _get_clothing_asset_count(asset)
            props.recompute_normals = _get_build_settings(asset, "recompute_normals")
            props.recompute_tangents = _get_build_settings(asset, "recompute_tangents")
            props.mikk_t_space = _get_mikk_t_space(asset)
            props.remove_degenerates = _get_build_settings(asset, "remove_degenerates")
            props.has_degenerates_triangles = _has_degenerates_triangles(asset)
            props.has_tangents_vertex_mask = _has_tangents_vertex_mask_channel(asset)
            props.materials, props.slot_section_usage = _get_materials_properties(asset)
            props.mesh_bones_hierarchy = _get_mesh_bones_hierarchy(asset)
            props.reference_bones_hierarchy = _get_reference_bones_hierarchy(asset)
        return props
