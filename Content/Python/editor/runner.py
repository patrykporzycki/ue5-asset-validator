import unreal
from editor.adapter import get_asset_properties
from core.types import Report, FixResult
from core.validator import validate
from editor.fixer import fix_mipmaps, fix_power_of_two, fix_max_resolution, fix_srgb, fix_compression

CHECK_TO_FIXER = {
    "srgb": fix_srgb,
    "compression": fix_compression,
    "mipmaps": fix_mipmaps,
    "max_resolution": fix_max_resolution,
    "power_of_two": fix_power_of_two,
}

_MEMORY_BUDGET = 256 * 1024 * 1024

def audit(asset_datas: unreal.AssetData, rules: dict):
    reports = []
    for asset_data in asset_datas:
        properties = get_asset_properties(asset_data)
        alerts = validate(properties, rules)
        report = Report(asset_data.package_name,
                        asset_data.asset_name,
                        asset_data.asset_class_path.asset_name,
                        properties["estimated_size"],
                        alerts)
        reports.append(report)
    return reports

def fix(reports: list, rules: dict):
    accumulated_bytes = 0
    fix_results = []
    with unreal.ScopedSlowTask(len(reports), "Fixing Assets") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        for report in reports:
            if slow_task.should_cancel():
                unreal.log_warning("Scan cancelled")
                break
            try:
                asset = unreal.EditorAssetLibrary.load_asset(str(report.path))
                for alert in report.alerts:
                    if rules["allow_autofix"].get(alert.id, False):
                        CHECK_TO_FIXER[alert.id](asset, alert)
                        fix_result = FixResult(report.name,alert.id, "fixed")
                        fix_results.append(fix_result)
                    else:
                        fix_result = FixResult(report.name, alert.id, "skipped")
                        fix_results.append(fix_result)
                unreal.EditorAssetLibrary.save_loaded_asset(asset)
                accumulated_bytes += report.estimated_size
                slow_task.enter_progress_frame(1)
                if accumulated_bytes > _MEMORY_BUDGET:
                    unreal.SystemLibrary.collect_garbage()
                    accumulated_bytes = 0
            except Exception as e:
                unreal.log_error("Failed to fix asset", e)
                for alert in report.alerts:
                    fix_result = FixResult(report.name, alert.id, "failed", str(e))
                    fix_results.append(fix_result)
    return fix_results