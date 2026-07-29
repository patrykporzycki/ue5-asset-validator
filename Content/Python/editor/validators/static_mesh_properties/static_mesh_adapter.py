from dataclasses import dataclass

import unreal
from core.types import AssetAdapter, BaseProps


@dataclass
class StaticMeshProps(BaseProps):
    triangles: int = 0
    materials: int = 0
    lods: int = 0
    collisions: int = 0
    nanite: bool = False


class StaticMeshPropsAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset = None):
        return StaticMeshProps(
            name=str(asset_data.asset_name),
            triangles=int(self.get_tag(asset_data, "Triangles") or 0),
            materials=int(self.get_tag(asset_data, "Materials") or 0),
            lods=int(self.get_tag(asset_data, "LODs") or 0),
            collisions=int(self.get_tag(asset_data, "CollisionPrims") or 0),
            nanite=bool(self.get_tag(asset_data, "NaniteEnabled") or 0),
        )
