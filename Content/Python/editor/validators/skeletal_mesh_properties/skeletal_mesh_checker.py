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

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['lods'] == 1 :
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"LODs are not set!",
                current_value=str(props['lods']),
                correct_value=None
            )
        return None

class BoneInfluencesCheck(Check):
    alert_id = "bone_influences"
    severity = Severity.WARNING
    is_fixable = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['max_bone_influences'] > rules['max_bone_influences'] :
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Max bone influence is bigger than {rules['max_bone_influences']}!",
                current_value=str(props['max_bone_influences']),
                correct_value=rules['max_bone_influences']
            )
        return None

    def fix(self, asset, alert):
        SkinWeightModifier = unreal.SkinWeightModifier()
        if not SkinWeightModifier.set_skeletal_mesh(asset):
            raise RuntimeError(f"Failed to load skeletal mesh for weight editing")
        SkinWeightModifier.enforce_max_influences(alert.correct_value)
        SkinWeightModifier.commit_weights_to_skeletal_mesh()
        unreal.log(f"Fixed bone influences for asset {asset.get_fname()}. Reduced from {alert.current_value} to {alert.correct_value}")

        return True

class ClothPhysicsCheck(Check):
    alert_id = "cloth_physics"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props["clothing_assets_count"] > 0 and props["physics_asset"] == "None":
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Clothing assets are not set!",
                current_value=props["physics_asset"],
                correct_value=None
            )
        return None

    def fix(self, asset, alert):
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

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['recompute_normals']:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Recompute Normals is enabled in build settings!",
                current_value=props['recompute_normals'],
                correct_value=False
            )
        return None

    def fix(self, asset, alert):
        _fix_build_setting(asset, "recompute_normals", alert.correct_value)
        unreal.log(f"Set recompute_normals false for asset {asset.get_fname()}")
        return True

class RecomputeTangentsCheck(Check):
    alert_id = "recompute_tangents"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        if props['recompute_tangents']:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Recompute Tangents is enabled in build settings!",
                current_value=props['recompute_tangents'],
                correct_value=False
            )
        return None

    def fix(self, asset, alert):
        _fix_build_setting(asset, "recompute_tangents", alert.correct_value)
        unreal.log(f"Set recompute_tangents false for asset {asset.get_fname()}")
        return True

class UseMikkTSpace(Check):
    alert_id = "mikk_t_space"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        if not props['mikk_t_space']:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Use mikk_t_space is disabled in build settings!",
                current_value=props['mikk_t_space'],
                correct_value=True
            )
        return None

    def fix(self, asset, alert):
        _fix_build_setting(asset, "use_mikk_t_space", alert.correct_value)
        unreal.log(f"Set use_mikk_t_space true for asset {asset.get_fname()}")
        return True

class UnusedMaterialSlotsCheck(Check):
    alert_id = "unused_material_slots"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        unused = [m for m  in props['materials'] if not m ["is_used"]]
        if unused:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Unused materials slots: {len(unused)}!",
                current_value=str(len(unused)),
                correct_value=0
            )
        return None

    def fix(self, asset, alert):
        SkeletalMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)

        used_slots = set()
        for lod in range(SkeletalMeshEditorSubsystem.get_lod_count(asset)):
            for section in range(SkeletalMeshEditorSubsystem.get_num_sections(asset, lod)):
                slot_index = SkeletalMeshEditorSubsystem.get_lod_material_slot(asset, lod, section)
                if slot_index >= 0:
                    used_slots.add(slot_index)

        materials = asset.get_editor_property("materials")
        new_materials = []
        for i, material in enumerate(materials):
            if i in used_slots:
                new_materials.append(material)

        asset.set_editor_property("materials", new_materials)
        unreal.log(f"Removed {len(materials) - len(new_materials)} unused material slots from {asset.get_fname()}")
        return True

class BoneNamesCheck(Check):
    alert_id = "bones_names"
    severity = Severity.WARNING
    is_fixable = True
    requires_deep = True

    def check(self, props: dict, rules: dict) -> Alert | None:
        reference_bones = set(props['reference_bones'])
        extra = [bone for bone in props['mesh_bones'] if bone not in reference_bones]
        if extra:
            return Alert(
                id=self.alert_id,
                severity=self.severity,
                message=f"Bones not in reference skeleton: {', '.join(extra)}",
                current_value=str(len(extra)),
                correct_value=0,
            )
        return None

    def fix(self, asset, alert):

        skeleton = asset.get_editor_property("skeleton")
        reference_bones = set(skeleton.get_reference_pose().get_bone_names())

        skeleton_modifier = unreal.SkeletonModifier()
        skeleton_modifier.set_skeletal_mesh(asset)
        mesh_bones = skeleton_modifier.get_all_bone_names()

        extra = [bone for bone in mesh_bones if bone not in reference_bones]
        for bone in extra:
            clean = re.sub(r"_\d+$", "", str(bone))
            if unreal.Name(clean) in reference_bones:
                skeleton_modifier.rename_bone(bone, unreal.Name(clean))

        skeleton_modifier.commit_skeleton_to_skeletal_mesh()
        unreal.log(f"Renamed {len(extra)} bones from {asset.get_fname()}")
        return True



SKELETAL_MESH_CHECKS = [
    LODsCheck(),
    BoneInfluencesCheck(),
    ClothPhysicsCheck(),
    RecomputeNormalsCheck(),
    RecomputeTangentsCheck(),
    UseMikkTSpace(),
    UnusedMaterialSlotsCheck(),
    BoneNamesCheck()
]
