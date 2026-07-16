import unreal
from core.types import AssetAdapter

def _parse_dimensions(dimensions: str):
    if "x" not in dimensions:
        return 0, 0
    parts = dimensions.split("x")
    return int(parts[0]), int(parts[1])

class TextureAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        dimensions = _parse_dimensions(self.get_tag(asset_data, "Dimensions"))
        asset_properties = {
            "name": str(asset_data.asset_name),
            "resolution_x": int(dimensions[0]),
            "resolution_y": int(dimensions[1]),
            "compression": self.get_tag(asset_data, "CompressionSettings").upper(),
            "alpha": self.get_tag(asset_data, "HasAlphaChannel").upper(),
            "srgb": self.get_tag(asset_data, "SRGB") == "True",
            "mipmaps": self.get_tag(asset_data, "MipGenSettings"),
            "estimated_size": int(dimensions[0]) * int(dimensions[1]) * 4
        }
        return asset_properties