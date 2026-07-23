import unreal
from core.types import AssetAdapter

class NamingConventionAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        asset_properties = {
            "name": str(asset_data.asset_name),
            "asset_class": str(asset_data.asset_class_path.asset_name),
            "estimated_size": 0
        }
        return asset_properties