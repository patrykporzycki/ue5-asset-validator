import unreal
from core.types import AssetAdapter


class StaticMeshAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        dimensions = self.get_tag(asset_data, "EstTotalCompressedSize") or 0
        asset_properties = {
            "name": str(asset_data.asset_name),
            "triangles": int(self.get_tag(asset_data, "Triangles") or 0),
            "materials": int(self.get_tag(asset_data, "Materials") or 0),
            "lods": int(self.get_tag(asset_data, "LODs") or 0),
            "collisions": int(self.get_tag(asset_data, "CollisionPrims") or 0),
            "nanite": bool(self.get_tag(asset_data, "NaniteEnabled") or 0),
            "estimated_size": int(dimensions),
        }
        return asset_properties