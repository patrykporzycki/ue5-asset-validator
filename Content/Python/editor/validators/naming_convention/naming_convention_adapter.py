from dataclasses import dataclass

import unreal
from core.types import AssetAdapter, BaseProps


@dataclass
class NamingProps(BaseProps):
    asset_class: str = ""


class NamingConventionAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        return NamingProps(
            name=str(asset_data.asset_name),
            asset_class=str(asset_data.asset_class_path.asset_name),
        )
