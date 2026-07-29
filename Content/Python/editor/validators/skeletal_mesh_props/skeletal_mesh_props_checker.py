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


class BoneNamesCheck(Check):
    alert_id = "bones_names"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props, rules) -> Alert | None:
        reference_bones = set(props.reference_bones)
        extra = [bone for bone in props.mesh_bones if bone not in reference_bones]
        if not extra:
            return None

        mesh_bones_set = set(props.mesh_bones)
        fixable = []
        for bone in extra:
            clean = re.sub(r"_\d+$", "", bone)
            if clean in reference_bones and clean not in mesh_bones_set:
                fixable.append((bone, clean))

        return Alert(
            id=self.alert_id,
            severity=self.severity,
            message=f"Bones not in reference skeleton: {', '.join(extra)}",
            current_value=str(len(extra)),
            correct_value=fixable
        )

    def fix(self, asset, alert, props):
        skeleton_modifier = unreal.SkeletonModifier()
        skeleton_modifier.set_skeletal_mesh(asset)
        for bone, clean in alert.correct_value:
            skeleton_modifier.rename_bone(unreal.Name(bone), unreal.Name(clean))
        skeleton_modifier.commit_skeleton_to_skeletal_mesh()
        unreal.log(f"Renamed {len(alert.correct_value)} bones from {asset.get_fname()}")
        return True


SKELETAL_MESH_PROPS_CHECKS = [
    LODsCheck(),
    BoneInfluencesCheck(),
    ClothPhysicsCheck(),
    RecomputeNormalsCheck(),
    RecomputeTangentsCheck(),
    UseMikkTSpace(),
    UnusedMaterialSlotsCheck(),
    BoneNamesCheck()
]
