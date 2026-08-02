from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity
import re

try:
    import unreal
except ImportError:
    unreal = None

def _fix_build_setting(asset, property_name, value):
    SkeletalMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    for i in range(SkeletalMeshEditorSubsystem.get_lod_count(asset)):
        build_settings = SkeletalMeshEditorSubsystem.get_lod_build_settings(asset, i)
        build_settings.set_editor_property(property_name, value)
        SkeletalMeshEditorSubsystem.set_lod_build_settings(asset, i, build_settings)

class LODsCheck(Check):
    alert_id = "lods"
    severity = Severity.WARNING

    def check(self, props, rules) -> Alert | None:
        if props.lods == 1:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="LODs are not set!",
                current_value=str(props.lods),
            )
        return None


class BoneInfluencesCheck(Check):
    alert_id = "bone_influences"
    severity = Severity.WARNING
    is_fixable = True

    def check(self, props, rules) -> Alert | None:
        if props.max_bone_influences > rules["max_bone_influences"]:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Max bone influence is bigger than {rules['max_bone_influences']}!",
                current_value=str(props.max_bone_influences),
                correct_value=rules["max_bone_influences"],
            )
        return None

    def fix(self, asset, alert, props):
        SkinWeightModifier = unreal.SkinWeightModifier()
        if not SkinWeightModifier.set_skeletal_mesh(asset):
            raise RuntimeError("Failed to load skeletal mesh for weight editing")
        SkinWeightModifier.enforce_max_influences(alert.correct_value)
        SkinWeightModifier.commit_weights_to_skeletal_mesh()
        unreal.log(f"Fixed bone influences for asset {asset.get_fname()}. Reduced from {alert.current_value} to {alert.correct_value}")
        return True


class ClothPhysicsCheck(Check):
    alert_id = "cloth_physics"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        if props.clothing_assets_count > 0 and props.physics_asset == "None":
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="Clothing assets are not set!",
                current_value=props.physics_asset,
            )
        return None

    def fix(self, asset, alert, props):
        SkeletalMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
        physics_asset = SkeletalMeshEditorSubsystem.create_physics_asset(asset, set_to_mesh=True, lod_index=0)
        if not physics_asset:
            raise RuntimeError(f"Failed to assign physics asset to asset {asset}!")
        unreal.EditorAssetLibrary.save_asset(physics_asset.get_path_name())
        unreal.log(f"Created physics asset for asset {asset.get_fname()}")
        return True


class RecomputeNormalsCheck(Check):
    alert_id = "recompute_normals"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        if props.recompute_normals:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="Recompute Normals is enabled in build settings!",
                current_value=str(props.recompute_normals),
                correct_value=False,
            )
        return None

    def fix(self, asset, alert, props):
        _fix_build_setting(asset, "recompute_normals", alert.correct_value)
        unreal.log(f"Set recompute_normals false for asset {asset.get_fname()}")
        return True


class RecomputeTangentsCheck(Check):
    alert_id = "recompute_tangents"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        if props.recompute_tangents:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="Recompute Tangents is enabled in build settings!",
                current_value=str(props.recompute_tangents),
                correct_value=False,
            )
        return None

    def fix(self, asset, alert, props):
        _fix_build_setting(asset, "recompute_tangents", alert.correct_value)
        unreal.log(f"Set recompute_tangents false for asset {asset.get_fname()}")
        return True


class UseMikkTSpace(Check):
    alert_id = "mikk_t_space"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        if not props.mikk_t_space:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message="Use mikk_t_space is disabled in build settings!",
                current_value=str(props.mikk_t_space),
                correct_value=True,
            )
        return None

    def fix(self, asset, alert, props):
        _fix_build_setting(asset, "use_mikk_t_space", alert.correct_value)
        unreal.log(f"Set use_mikk_t_space true for asset {asset.get_fname()}")
        return True


class UnusedMaterialSlotsCheck(Check):
    alert_id = "unused_material_slots"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        unused = [
            material for index, material in enumerate(props.materials)
            if index not in props.slot_section_usage
        ]
        if not unused:
            return None
        return Alert(
            id=self.alert_id,
            severity=self.severity,
            message=f"Unused materials slots: {len(unused)}!",
            current_value=str(len(unused)),
        )

    def fix(self, asset, alert, props):
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

class BoneNamesCheck(Check):
    alert_id = "bones_names"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        fixable, hierarchy_mismatch, not_in_ref = _categorize_extra_bones(props)
        if fixable:
            bones, clean_bones = zip(*fixable)
            bones = list(bones)
            clean_bones = list(clean_bones)
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Bones with invalid names: {bones}!",
                current_value=bones,
                correct_value=clean_bones,
            )
        return None

    def fix(self, asset, alert, props):
        skeleton_modifier = unreal.SkeletonModifier()
        if not skeleton_modifier.set_skeletal_mesh(asset):
            raise RuntimeError("Failed to load skeletal mesh for bone renaming!")
        for bone, clean in zip(alert.current_value, alert.correct_value):
            skeleton_modifier.rename_bone(unreal.Name(bone), unreal.Name(clean))
        skeleton_modifier.commit_skeleton_to_skeletal_mesh()
        unreal.log(f"Renamed {len(alert.current_value)} bones!")
        return True


class BoneHierarchyMismatchCheck(Check):
    alert_id = "bones_hierarchy_mismatch"
    severity = Severity.WARNING
    is_fixable = False
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        fixable, hierarchy_mismatch, not_in_ref = _categorize_extra_bones(props)
        if hierarchy_mismatch:
            bones, clean_bones = zip(*hierarchy_mismatch)
            bones = list(bones)
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Bones with wrong hierarchy: {bones}!",
                current_value=bones,
                correct_value=None,
            )
        return None


class BoneNotInReferenceCheck(Check):
    alert_id = "bones_not_in_reference"
    severity = Severity.WARNING
    is_fixable = False
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        fixable, hierarchy_mismatch, not_in_ref = _categorize_extra_bones(props)
        if not_in_ref:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Extra bones not in reference skeleton: {not_in_ref}!",
                current_value=not_in_ref,
                correct_value=None,
            )
        return None

SKELETAL_MESH_PROPS_CHECKS = [
    LODsCheck(),
    BoneInfluencesCheck(),
    ClothPhysicsCheck(),
    RecomputeNormalsCheck(),
    RecomputeTangentsCheck(),
    UseMikkTSpace(),
    UnusedMaterialSlotsCheck(),
    BoneNamesCheck(),
    BoneHierarchyMismatchCheck(),
    BoneNotInReferenceCheck(),
]
