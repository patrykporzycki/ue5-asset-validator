import unreal
from core.types import AssetAdapter

class TextureAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        dimensions = asset_data.get_tag_value("Dimensions")
        asset_properties = {
            "name": str(asset_data.asset_name),
            "resolution_x": int(dimensions.split("x")[0]),
            "resolution_y": int(dimensions.split("x")[1]),
            "compression": asset_data.get_tag_value("CompressionSettings").upper(),
            "srgb": asset_data.get_tag_value("SRGB") == "True",
            "mipmaps": asset_data.get_tag_value("MipGenSettings"),
            "estimated_size": int(dimensions.split("x")[0]) * int(dimensions.split("x")[1]) * 4
        }
        return asset_properties