import unreal
import pathlib

from core.rule_loader import load_rules
from editor.scanner import scan_folders
from editor.runner import audit, fix
from editor.registry import VALIDATOR_REGISTRY

def run(config_path = None, asset_paths = None):

    wildcard = any("*" in r.applies_to for r in VALIDATOR_REGISTRY.values())

    class_names = []
    if not wildcard:
        for registry in VALIDATOR_REGISTRY.values():
            for apply in registry.applies_to:
                if apply not in class_names and apply != "*":
                    class_names.append(apply)
    if asset_paths:
        asset_datas = scan_folders(asset_paths, class_names)
    else:
        selection = unreal.EditorUtilityLibrary.get_selected_assets()
        paths = {str(asset.get_path_name()) for asset in selection}
        folders = {unreal.Paths.get_path(p) for p in paths}
        scanned_asset_datas = scan_folders(folders, class_names)
        asset_datas = [a for a in scanned_asset_datas if str(a.package_name) + "." + str(a.asset_name) in paths]


    if len(asset_datas) == 0:
        unreal.log("Nothing selected!")
        return

    if config_path is None:
        config_path = pathlib.Path(__file__).parent / "config" / "validation_rules.json"

    try:
        rules = load_rules(config_path)
    except (FileNotFoundError, ValueError) as e:
        unreal.log_error(str(e))
        return

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



