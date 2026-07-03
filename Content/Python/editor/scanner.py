import unreal
def scan_folders(paths):
    EditorAssetLibrary = unreal.EditorAssetLibrary
    assets = []
    for path in paths:
        asset_paths = EditorAssetLibrary.list_assets(path, recursive=True)
        total_steps = len(asset_paths)
        with unreal.ScopedSlowTask(total_steps, "Scanning Assets") as slow_task:
            slow_task.make_dialog(can_cancel=True)
            for asset_path in asset_paths:
                if slow_task.should_cancel():
                    unreal.log_warning("Scan cancelled")
                    break
                asset = EditorAssetLibrary.load_asset(asset_path)
                if isinstance(asset, unreal.Texture2D):
                    assets.append(asset)
                slow_task.enter_progress_frame(1)

    return assets