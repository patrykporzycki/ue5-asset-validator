import unreal
from core.types import Report, FixResult
from editor.registry import VALIDATOR_REGISTRY
from core.validator import validate

_PACKAGE_BUDGET = 100

def audit(asset_datas: unreal.AssetData, rules: dict, validators=None):
    reports = []

    if validators is not None:
        active_validators = {}
        for k, v in VALIDATOR_REGISTRY.items():
            if k in validators:
                active_validators[k] = v
    else:
        active_validators = VALIDATOR_REGISTRY

    base_packages = unreal.PackageLoaderManager.get_loaded_package_names()

    with unreal.ScopedSlowTask(len(asset_datas), "Loading Assets") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        for asset_data in asset_datas:
            path = str(asset_data.package_name)
            try:
                asset_class = str(asset_data.asset_class_path.asset_name)
                needs_u_object = False
                for active_validator in active_validators.values():
                    if asset_class in active_validator.applies_to or "*" in active_validator.applies_to:
                        if active_validator.adapter.requires_u_object:
                            needs_u_object = True
                            break

                asset = None
                slow_task.enter_progress_frame(1, f"Loading: {path}")
                if needs_u_object:
                    asset = unreal.find_asset(path) or unreal.EditorAssetLibrary.load_asset(str(path))

                for validator_name, validator in active_validators.items():
                    if asset_class not in validator.applies_to and "*" not in validator.applies_to:
                        continue
                    try:
                        asset_for_adapter = asset if validator.adapter.requires_u_object else None
                        properties = validator.adapter.get_properties(asset_data, asset_for_adapter)
                        alerts = validate(properties, rules, validator.checks)
                        if alerts:
                            report = Report(asset_data.package_name,
                                            properties["name"],
                                            asset_class,
                                            properties["estimated_size"],
                                            alerts)
                            reports.append(report)
                    except Exception as e:
                        unreal.log_warning(f"Validator {validator_name} failed to audit asset {asset_data.asset_class_path.asset_name} : {e}")
                        continue

                if needs_u_object:
                    current_packages = unreal.PackageLoaderManager.get_loaded_package_count()
                    if current_packages - len(base_packages) > _PACKAGE_BUDGET:
                        asset = None
                        unreal.PackageLoaderManager.unload_loaded_packages(base_packages)
                        unreal.SystemLibrary.collect_garbage()

            except Exception as e:
                unreal.log_warning(f"Failed to audit asset {asset_data.asset_class_path.asset_name}", e)
                continue
    unreal.PackageLoaderManager.unload_loaded_packages(base_packages)
    unreal.SystemLibrary.collect_garbage()
    return reports


def fix(reports: list):
    fix_results = []
    reports_by_path = {}
    for report in reports:
        if report.path in reports_by_path:
            reports_by_path[report.path].append(report)
        else:
            reports_by_path[report.path] = [report]

    base_packages = unreal.PackageLoaderManager.get_loaded_package_names()

    with unreal.ScopedSlowTask(len(reports_by_path), "Fixing Assets") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        for path, grouped_reports in reports_by_path.items():
            if slow_task.should_cancel():
                break
            try:
                slow_task.enter_progress_frame(1, f"Fixing: {path}")
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

                current_packages = unreal.PackageLoaderManager.get_loaded_package_count()
                if current_packages - len(base_packages) > _PACKAGE_BUDGET:
                    unreal.PackageLoaderManager.unload_loaded_packages(base_packages)
                    unreal.SystemLibrary.collect_garbage()

            except Exception as e:
                unreal.log_error("Failed to fix asset", e)
                for report in grouped_reports:
                    for alert in report.alerts:
                        fix_result = FixResult(report.name, alert.id, "failed", str(e))
                        fix_results.append(fix_result)

    unreal.PackageLoaderManager.unload_loaded_packages(base_packages)
    unreal.SystemLibrary.collect_garbage()
    return fix_results
