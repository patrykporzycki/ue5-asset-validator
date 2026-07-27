import unreal
from core.types import AssetAdapter
from typing import Any


def _get_materials_properties(asset):
    used_slots = set()
    SkeletalMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    for lod in range(SkeletalMeshEditorSubsystem.get_lod_count(asset)):
        for section in range(SkeletalMeshEditorSubsystem.get_num_sections(asset, lod)):
            slot_index = SkeletalMeshEditorSubsystem.get_lod_material_slot(asset, lod, section)
            if slot_index >= 0:
                used_slots.add(slot_index)

    materials = asset.get_editor_property("materials")
    material_slots = []
    for i, material in enumerate(materials):
        material_interface = material.get_editor_property("material_interface")
        material_slots.append({
            "slot_name": material.get_editor_property("material_slot_name"),
            "material": material_interface.get_name() if material_interface else None,
            "is_used": i in used_slots,
        })
    return {"materials": material_slots}

def _get_build_settings(asset):
    recompute_normals = False
    recompute_tangents = False
    mikk_t_space = True

    for model in (asset.get_editor_property("source_models")):
        build_settings = model.get_editor_property("build_settings")
        if build_settings.get_editor_property('recompute_normals'):
            recompute_normals = True
        if build_settings.get_editor_property('recompute_tangents'):
            recompute_tangents = True
        if not build_settings.get_editor_property('use_mikk_t_space'):
            mikk_t_space = False

    return {"recompute_normals": recompute_normals,
            "recompute_tangents": recompute_tangents,
            "mikk_t_space": mikk_t_space,}

def _get_clothing_asset_count(asset):
    clothing_asset_count = len(asset.get_editor_property("mesh_clothing_assets"))
    return {"clothing_assets_count": clothing_asset_count}

def _get_skeleton_bone_names(asset):
    skeleton = asset.get_editor_property("skeleton")
    if not skeleton:
        return {"mesh_bones": [], "reference_bones": []}
    reference_bones = [str(bone) for bone in skeleton.get_reference_pose().get_bone_names()]
    SkeletonModifier = unreal.SkeletonModifier()
    SkeletonModifier.set_skeletal_mesh(asset)
    mesh_bones = [str(bone) for bone in SkeletonModifier.get_all_bone_names()]
    return {"mesh_bones": mesh_bones, "reference_bones": reference_bones}


class SkeletalMeshAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        dimensions = self.get_tag(asset_data, "EstTotalCompressedSize") or 0
        asset_properties: dict[str, Any] = {
            "name": str(asset_data.asset_name),
            "triangles": int(self.get_tag(asset_data, "Triangles") or 0),
            "lods": int(self.get_tag(asset_data, "LODs") or 0),
            "bones": int(self.get_tag(asset_data, "Bones") or 0),
            "max_bone_influences": int(self.get_tag(asset_data, "MaxBoneInfluences") or 0),
            "skeleton": str(self.get_tag(asset_data, "Skeleton")),
            "physics_asset": str(self.get_tag(asset_data, "PhysicsAsset")),
            "morphs": int(self.get_tag(asset_data, "MorphTargets") or 0),
            "estimated_size": int(dimensions),
        }
        if asset:
            asset_properties.update(_get_clothing_asset_count(asset))
            asset_properties.update(_get_build_settings(asset))
            asset_properties.update(_get_materials_properties(asset))
            asset_properties.update(_get_skeleton_bone_names(asset))
        return asset_properties
