import unreal

def scan_folders(paths):

    ar_filter = unreal.ARFilter(
        package_paths=paths,
        recursive_paths=True,
        class_names=["Texture2D"]
    )

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_datas = registry.get_assets(ar_filter)
    assets = []
    total_steps = len(asset_datas)

    with unreal.ScopedSlowTask(total_steps, "Scanning Assets") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        for a in asset_datas:
            if slow_task.should_cancel():
                unreal.log_warning("Scan cancelled")
                break
            asset = a.get_asset()
            assets.append(asset)
            slow_task.enter_progress_frame(1)
    return assets