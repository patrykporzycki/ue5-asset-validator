import unreal
from core.types import AssetAdapter

class MaterialPropertiesAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        asset_properties = {
            "name": str(asset_data.asset_name),
            "blend_mode": str(self.get_tag(asset_data, "BlendMode")),
            "shading_models": str(self.get_tag(asset_data, "ShadingModels")),
            "material_domain": str(self.get_tag(asset_data, "MaterialDomain")),
            "estimated_size": 250,
        }
        print(asset_properties)
        return asset_properties