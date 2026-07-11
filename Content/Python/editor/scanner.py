import unreal

def scan_folders(paths, class_names):

    ar_filter = unreal.ARFilter(
        package_paths=paths,
        recursive_paths=True,
        class_names=class_names,
    )

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_datas = registry.get_assets(ar_filter)
    return asset_datas or []