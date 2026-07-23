import unreal
from core.types import Report, FixResult
from editor.registry import VALIDATOR_REGISTRY
from core.validator import validate

_MEMORY_BUDGET = 256 * 1024 * 1024

def audit(asset_datas: unreal.AssetData, rules: dict, validators=None, deep=False):
    reports = []
    loaded_assets = {}
    accumulated_bytes = 0
    if validators is not None:
        active_validators = {}
        for k, v in VALIDATOR_REGISTRY.items():
            if k in validators:
                active_validators[k] = v
    else:
        active_validators = VALIDATOR_REGISTRY
    for asset_data in asset_datas:
        try:
            asset_class = str(asset_data.asset_class_path.asset_name)
            just_loaded = False
            for validator_name, validator in active_validators.items():
                asset = None
                try:
                    if asset_class in validator.applies_to or "*" in validator.applies_to:
                        if validator.adapter.requires_u_object and deep:
                            path = str(asset_data.package_name)
                            if path not in loaded_assets:
                                asset = unreal.EditorAssetLibrary.load_asset(path)
                                loaded_assets[path] = asset
                                just_loaded = True
                            else:
                                asset = loaded_assets[path]

                        properties = validator.adapter.get_properties(asset_data, asset)
                        alerts = validate(properties, rules, validator.checks)
                        report = Report(asset_data.package_name,
                                        properties["name"],
                                        asset_class,
                                        properties["estimated_size"],
                                        alerts)
                        reports.append(report)

                        if asset and just_loaded:
                            accumulated_bytes += properties["estimated_size"]
                            just_loaded = False
                        if accumulated_bytes > _MEMORY_BUDGET:
                            unreal.SystemLibrary.collect_garbage()
                            accumulated_bytes = 0

                except Exception as e:
                    unreal.log_warning(f"Validator {validator_name} failed to audit asset {asset_data.asset_class_path.asset_name}", e)
                    continue
        except Exception as e:
            unreal.log_warning(f"Failed to audit asset {asset_data.asset_class_path.asset_name}", e)
            continue
    return reports

def fix(reports: list):
    accumulated_bytes = 0
    fix_results = []
    reports_by_path = {}
    for report in reports:
        if report.path in reports_by_path:
            reports_by_path[report.path].append(report)
        else:
            reports_by_path[report.path] = [report]

    with unreal.ScopedSlowTask(len(reports_by_path), "Fixing Assets") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        with unreal.ScopedEditorTransaction("Fixing Assets"):
            for path, grouped_reports in reports_by_path.items():
                if slow_task.should_cancel():
                    break
                try:
                    asset = unreal.EditorAssetLibrary.load_asset(str(path))
                    save_fixed = False
                    for grouped_report in grouped_reports:
                        for alert in grouped_report.alerts:
                            fixed = False
                            for validator_name, validator in VALIDATOR_REGISTRY.items():
                                if grouped_report.type in validator.applies_to or "*" in validator.applies_to:
                                    for check in validator.checks:
                                        if check.is_fixable and check.alert_id == alert.id:
                                            try:
                                                check.fix(asset, alert)
                                                fix_result = FixResult(grouped_report.name, alert.id, "fixed")
                                            except Exception as e:
                                                fix_result = FixResult(grouped_report.name, alert.id, "failed", f"Failed to fix asset. {e}")
                                            fix_results.append(fix_result)
                                            fixed = True
                                            save_fixed = True
                                            break
                                if fixed:
                                    break
                            if not fixed:
                                fix_result = FixResult(grouped_report.name, alert.id, "skipped")
                                fix_results.append(fix_result)
                    if save_fixed:
                        unreal.EditorAssetLibrary.save_loaded_asset(asset)
                    accumulated_bytes += max(report.estimated_size for report in grouped_reports)
                    slow_task.enter_progress_frame(1)
                    if accumulated_bytes > _MEMORY_BUDGET:
                        unreal.SystemLibrary.collect_garbage()
                        accumulated_bytes = 0
                except Exception as e:
                    unreal.log_error("Failed to fix asset", e)
                    for report in grouped_reports:
                        for alert in report.alerts:
                            fix_result = FixResult(report.name, alert.id, "failed", str(e))
                            fix_results.append(fix_result)
    return fix_results
