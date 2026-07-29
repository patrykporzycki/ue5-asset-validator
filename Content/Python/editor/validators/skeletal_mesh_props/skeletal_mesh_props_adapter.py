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
    return None


def _get_clothing_asset_count(asset):
    clothing_asset_count = len(asset.get_editor_property("mesh_clothing_assets"))
    return clothing_asset_count


def _get_reference_bones(asset) -> list[str]:
    skeleton = asset.get_editor_property("skeleton")
    if not skeleton:
        return []
    return [str(bone) for bone in skeleton.get_reference_pose().get_bone_names()]


def _get_mesh_bones(asset) -> list[str]:
    SkeletonModifier = unreal.SkeletonModifier()
    SkeletonModifier.set_skeletal_mesh(asset)
    return [str(bone) for bone in SkeletonModifier.get_all_bone_names()]


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
    recompute_normals: bool | None = None
    recompute_tangents: bool | None = None
    mikk_t_space: bool | None = None
    materials: list | None = None
    slot_section_usage: dict[int, set[int]] | None = None
    mesh_bones: list[str] | None = None
    reference_bones: list[str] | None = None


class SkeletalMeshPropsAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None) -> SkeletalMeshProps:
        props = SkeletalMeshProps(
            name = str(asset_data.asset_name),
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
            props.materials, props.slot_section_usage = _get_materials_properties(asset)
            props.reference_bones = _get_reference_bones(asset)
            props.mesh_bones = _get_mesh_bones(asset)
        return props
