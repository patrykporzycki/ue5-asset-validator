from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity
from editor.validators.mesh_checks.mesh_checks import MESH_CHECKS
import re

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

class BoneInfluencesCheck(Check):
    check_id = "bone_influences"

    def check(self, props, config) -> list[Alert]:
        max_bone_influences = config["params"]["max_bone_influences"]
        if props.max_bone_influences > max_bone_influences:
            return [Alert(
                id="bone_influences",
                severity=Severity.ERROR,
                message=f"Max bone influence is bigger than {max_bone_influences}!",
                current_value=str(props.max_bone_influences),
                correct_value=max_bone_influences,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        SkinWeightModifier = unreal.SkinWeightModifier()
        if not SkinWeightModifier.set_skeletal_mesh(asset):
            raise RuntimeError("Failed to load skeletal mesh for weight editing")
        SkinWeightModifier.enforce_max_influences(alert.correct_value)
        SkinWeightModifier.commit_weights_to_skeletal_mesh()
        unreal.log(f"Fixed bone influences for asset {asset.get_fname()}. Reduced from {alert.current_value} to {alert.correct_value}")
        return True


class ClothPhysicsCheck(Check):
    check_id = "cloth_physics"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        if props.clothing_assets_count > 0 and props.physics_asset == "None":
            return [Alert(
                id="cloth_physics",
                severity=Severity.WARNING,
                message="Clothing assets are not set!",
                current_value=props.physics_asset,
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, props=None, options=None):
        SkeletalMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
        physics_asset = SkeletalMeshEditorSubsystem.create_physics_asset(asset, set_to_mesh=True, lod_index=0)
        if not physics_asset:
            raise RuntimeError(f"Failed to assign physics asset to asset {asset}!")
        unreal.EditorAssetLibrary.save_asset(physics_asset.get_path_name())
        unreal.log(f"Created physics asset for asset {asset.get_fname()}")
        return True

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
        materials = asset.get_editor_property("materials")
        used_indices = set(props.slot_section_usage.keys())
        new_materials = [material for index, material in enumerate(materials) if index in used_indices]
        asset.set_editor_property("materials", new_materials)
        unreal.log(f"Removed {len(materials) - len(new_materials)} unused material slots from {asset.get_fname()}")
        return True


def _ancestor_chain(name: str, parents: dict):
    chain = []
    current = parents.get(name)
    visited: set[str] = set()
    while current and current not in visited:
        visited.add(current)
        chain.append(current)
        current = parents.get(current)
    return tuple(chain)


def _hierarchy_matches(bone: str, clean: str, mesh_parents: dict, ref_parents: dict):
    bone_chain = _ancestor_chain(bone, mesh_parents)
    clean_chain = _ancestor_chain(clean, ref_parents)

    bone_stripped = tuple(re.sub(r"_\d+$", "", b) for b in bone_chain)
    clean_stripped = tuple(re.sub(r"_\d+$", "", b) for b in clean_chain)

    return bone_stripped == clean_stripped


def _categorize_extra_bones(props):
    reference_bones = set(props.reference_bones_hierarchy or {})
    mesh_bones_set = set(props.mesh_bones_hierarchy or {})
    extra = [bone for bone in mesh_bones_set if bone not in reference_bones]

    fixable: list[tuple[str, str]] = []
    hierarchy_mismatch: list[tuple[str, str]] = []
    not_in_ref: list[str] = []

    for bone in extra:
        clean = re.sub(r"_\d+$", "", bone)
        if clean == bone or clean not in reference_bones:
            not_in_ref.append(bone)
        elif clean in mesh_bones_set:
            hierarchy_mismatch.append((bone, clean))
        elif _hierarchy_matches(bone, clean, props.mesh_bones_hierarchy, props.reference_bones_hierarchy):
            fixable.append((bone, clean))
        else:
            hierarchy_mismatch.append((bone, clean))

    return fixable, hierarchy_mismatch, not_in_ref


class BoneValidationCheck(Check):
    check_id = "bone_validation"
    requires_deep = True

    def check(self, props, config) -> list[Alert]:
        fixable, hierarchy_mismatch, not_in_ref = _categorize_extra_bones(props)
        alerts = []
        if fixable:
            bones, clean_bones = zip(*fixable)
            alerts.append(Alert(
                id="bones_names",
                severity=Severity.WARNING,
                message=f"Bones with invalid names: {list(bones)}!",
                current_value=list(bones),
                correct_value=list(clean_bones),
                is_fixable=True,
            ))
        if hierarchy_mismatch:
            bones, _ = zip(*hierarchy_mismatch)
            alerts.append(Alert(
                id="bones_hierarchy_mismatch",
                severity=Severity.ERROR,
                message=f"Bones with wrong hierarchy: {list(bones)}!",
                current_value=list(bones),
            ))
        if not_in_ref:
            alerts.append(Alert(
                id="bones_not_in_reference",
                severity=Severity.WARNING,
                message=f"Extra bones not in reference skeleton: {not_in_ref}!",
                current_value=not_in_ref,
            ))
        return alerts

    def fix(self, asset, alert, props=None, options=None):
        if alert.id != "bones_names":
            return False
        skeleton_modifier = unreal.SkeletonModifier()
        if not skeleton_modifier.set_skeletal_mesh(asset):
            raise RuntimeError("Failed to load skeletal mesh for bone renaming!")
        for bone, clean in zip(alert.current_value, alert.correct_value):
            skeleton_modifier.rename_bone(unreal.Name(bone), unreal.Name(clean))
        skeleton_modifier.commit_skeleton_to_skeletal_mesh()
        unreal.log(f"Renamed {len(alert.current_value)} bones!")
        return True

SKELETAL_MESH_PROPS_CHECKS = [
    *MESH_CHECKS,
    LODsCheck(),
    BoneInfluencesCheck(),
    ClothPhysicsCheck(),
    UnusedMaterialSlotsCheck(),
    BoneValidationCheck(),
]
