import unreal
import pathlib

from core.texture_checker import set_suffix_rules
from core.rule_loader import load_rules
from editor.scanner import scan_folders
from editor.runner import audit, fix

def run(config_path = None, asset_paths = None):

    if asset_paths:
        asset_datas = scan_folders(asset_paths)
    else:
        selection = unreal.EditorUtilityLibrary.get_selected_assets()
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        asset_datas=[]
        for asset in selection:
            if isinstance(asset, unreal.Texture2D):
                a = registry.get_asset_by_object_path(asset.get_path_name())
                asset_datas.append(a)

    if len(asset_datas) == 0:
        unreal.log("Nothing selected!")
        return

    if config_path is None:
        config_path = pathlib.Path(__file__).parent / "config" / "validation_rules.json"

    rules = load_rules(config_path)
    if rules is None:
        return
    set_suffix_rules(rules["suffix_rules"])

    unreal.log(f"Checking {len(asset_datas)} assets...")
    reported_assets = audit(asset_datas, rules)
    fixed_assets = fix(reported_assets, rules)

    for asset in reported_assets:
        for alert in asset.alerts:
            unreal.log(f"{asset.name}: {alert.message}")
        if not asset.alerts:
            unreal.log(f"{asset.name}: OK")

    fixed = sum(1 for f in fixed_assets if f.status == "fixed")
    skipped = sum(1 for f in fixed_assets if f.status == "skipped")
    failed = sum(1 for f in fixed_assets if f.status == "failed")
    unreal.log(f"Fix results: {fixed} fixed, {skipped} skipped, {failed} failed")

    for fixed_asset in fixed_assets:
        if fixed_asset.status == "failed":
            unreal.log_error(f"  {fixed_asset.name}: [{fixed_asset.alert}] — {fixed_asset.error}")



