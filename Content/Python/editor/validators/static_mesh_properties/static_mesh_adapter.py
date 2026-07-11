import unreal
from core.types import AssetAdapter


class StaticMeshAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        dimensions = self.get_tag(asset_data, "EstTotalCompressedSize")
        asset_properties = {
            "name": str(asset_data.asset_name),
            "lods": int(self.get_tag(asset_data, "LODs")),
            "collisions": int(self.get_tag(asset_data, "CollisionPrims")),
            "estimated_size": int(dimensions),
        }
        return asset_properties