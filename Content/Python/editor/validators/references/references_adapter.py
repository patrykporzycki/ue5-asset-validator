import unreal
from core.types import AssetAdapter

class ReferencesAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
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

        asset_properties = {
            "name": str(asset_data.asset_name),
            "asset_class": str(asset_data.asset_class_path.asset_name),
            "package_name": str(asset_data.package_name),
            "broken_references": broken_references,
            "referencers": referencers,
            "estimated_size": 0
        }
        return asset_properties