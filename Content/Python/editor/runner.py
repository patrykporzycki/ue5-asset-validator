import unreal
from core.types import Report, FixResult
from editor.registry import VALIDATOR_REGISTRY
from core.validator import validate

_MEMORY_BUDGET = 256 * 1024 * 1024

def audit(asset_datas: unreal.AssetData, rules: dict):
    reports = []
    for asset_data in asset_datas:
        asset_class = str(asset_data.asset_class_path.asset_name)
        for validator_name, validator in VALIDATOR_REGISTRY.items():
            if asset_class in validator.applies_to or "*" in validator.applies_to:
                properties = validator.adapter.get_properties(asset_data)
                alerts = validate(properties, rules, validator.checks)
                report = Report(asset_data.package_name,
                                properties["name"],
                                asset_class,
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
                save_fixed = False
                for alert in report.alerts:
                    fixed = False
                    if rules["allow_autofix"].get(alert.id, False):
                        for validator_name, validator in VALIDATOR_REGISTRY.items():
                            if report.type in validator.applies_to or "*" in validator.applies_to:
                                for check in validator.checks:
                                    if hasattr(check, 'fix') and check.alert_id == alert.id:
                                        check.fix(asset, alert)
                                        fix_result = FixResult(report.name,alert.id, "fixed")
                                        fix_results.append(fix_result)
                                        fixed = True
                                        save_fixed = True
                                        break
                            if fixed:
                                break
                        if not fixed:
                            fix_result = FixResult(report.name, alert.id, "skipped")
                            fix_results.append(fix_result)
                    else:
                        fix_result = FixResult(report.name, alert.id, "skipped")
                        fix_results.append(fix_result)
                if save_fixed:
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