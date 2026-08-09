from dataclasses import dataclass

import unreal
from core.types import AssetAdapter, BaseProps


@dataclass
class MaterialProps(BaseProps):
    blend_mode: str = ""
    shading_models: str = ""
    material_domain: str = ""


class MaterialPropsAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        return MaterialProps(
            name=str(asset_data.asset_name),
            blend_mode=str(self.get_tag(asset_data, "BlendMode")),
            shading_models=str(self.get_tag(asset_data, "ShadingModels")),
            material_domain=str(self.get_tag(asset_data, "MaterialDomain")),
        )
