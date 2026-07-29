from dataclasses import dataclass, field

import unreal
from core.types import AssetAdapter, BaseProps


@dataclass
class ReferencesProps(BaseProps):
    asset_class: str = ""
    package_name: str = ""
    broken_references: list[str] = field(default_factory=list)
    referencers: list = field(default_factory=list)


class ReferencesAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        references = registry.get_dependencies(asset_data.package_name, unreal.AssetRegistryDependencyOptions(
            include_hard_package_references=True,
            include_game_package_references=True
        ))
        broken_references = [str(r) for r in references if str(r).startswith("/Game/") and not unreal.EditorAssetLibrary.does_asset_exist(str(r))]

        referencers = registry.get_referencers(asset_data.package_name, unreal.AssetRegistryDependencyOptions(
            include_hard_package_references=True,
            include_game_package_references=True
        ))

        return ReferencesProps(
            name=str(asset_data.asset_name),
            asset_class=str(asset_data.asset_class_path.asset_name),
            package_name=str(asset_data.package_name),
            broken_references=broken_references,
            referencers=referencers,
        )
