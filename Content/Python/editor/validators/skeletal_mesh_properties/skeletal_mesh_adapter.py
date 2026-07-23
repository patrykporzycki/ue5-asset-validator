import unreal
from core.types import AssetAdapter

class SkeletalMeshAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        dimensions = self.get_tag(asset_data, "EstTotalCompressedSize") or 0
        asset_properties = {
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
        return asset_properties