from dataclasses import dataclass

import unreal
from core.types import AssetAdapter, BaseProps

def _get_mikk_t_space(asset) -> bool:
    for model in asset.get_editor_property("source_models"):
        build_settings = model.get_editor_property("build_settings")
        if not build_settings.get_editor_property("use_mikk_t_space"):
            return False
    return True

def _get_build_settings(asset, build_property):
    for model in (asset.get_editor_property("source_models")):
        build_settings = model.get_editor_property("build_settings")
        if build_settings.get_editor_property(build_property):
            return True
    return None

@dataclass
class StaticMeshProps(BaseProps):
    triangles: int = 0
    materials: int = 0
    lods: int = 0
    collisions: int = 0
    nanite: bool = False

    recompute_normals: bool | None = None
    recompute_tangents: bool | None = None
    mikk_t_space: bool | None = None

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
