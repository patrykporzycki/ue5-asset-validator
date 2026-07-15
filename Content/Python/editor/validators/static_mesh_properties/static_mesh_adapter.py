import unreal
from core.types import AssetAdapter


class StaticMeshAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        dimensions = self.get_tag(asset_data, "EstTotalCompressedSize") or 0
        asset_properties = {
            "name": str(asset_data.asset_name),
            "lods": int(self.get_tag(asset_data, "LODs") or 0),
            "collisions": int(self.get_tag(asset_data, "CollisionPrims") or 0),
            "estimated_size": int(dimensions),
        }
        return asset_properties