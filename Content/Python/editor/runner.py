import unreal
import os
from core.types import Report, FixResult
from editor.registry import VALIDATOR_REGISTRY
from core.validator import validate

_PACKAGE_BUDGET = 100

def _select_active_validators(validators = None):
    if validators is not None:
        active_validators = {}
        for k, v in VALIDATOR_REGISTRY.items():
            if k in validators:
                active_validators[k] = v
    else:
        active_validators = VALIDATOR_REGISTRY
    return active_validators

def _file_timestamp(path):
    try:
        file_path = unreal.PackageTools.package_name_to_filename(path, ".uasset")
        return os.path.getmtime(file_path)
    except (FileNotFoundError, OSError):
        return None

def audit(asset_datas: unreal.AssetData, rules: dict, validators=None):
    reports = []
    active_validators = _select_active_validators(validators)
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

                all_alerts = {}
                all_props = {}
                for validator_name, validator in active_validators.items():
                    if asset_class not in validator.applies_to and "*" not in validator.applies_to:
                        continue
                    try:
                        asset_for_adapter = asset if validator.adapter.requires_u_object else None
                        properties = validator.adapter.get_properties(asset_data, asset_for_adapter)
                        alerts = validate(properties, rules, validator.checks)
                        if alerts:
                            all_alerts[validator_name] = alerts
                            all_props[validator_name] = properties
                    except Exception as e:
                        unreal.log_warning(f"Validator {validator_name} failed to audit asset {asset_data.asset_class_path.asset_name} : {e}")
                        continue
                if all_alerts:
                    report = Report(path, str(asset_data.asset_name), asset_class, all_alerts, all_props, _file_timestamp(path))
                    reports.append(report)

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
    base_packages = unreal.PackageLoaderManager.get_loaded_package_names()

    with unreal.ScopedSlowTask(len(reports), "Fixing Assets") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        for report in reports:
            if slow_task.should_cancel():
                break
            try:
                slow_task.enter_progress_frame(1, f"Fixing: {report.path}")
                timestamp = _file_timestamp(report.path)
                if timestamp is None:
                    for source, results in report.alerts.items():
                        for alert, check in results:
                            fix_result = FixResult(report.name, alert.id, "failed", source, "Failed to load asset!")
                            fix_results.append(fix_result)
                    continue
                if timestamp > report.timestamp:
                    for source, results in report.alerts.items():
                        for alert, check in results:
                            fix_result = FixResult(report.name, alert.id, "skipped", source, "Skipped, asset changed since last scan!")
                            fix_results.append(fix_result)
                    continue
                asset = unreal.EditorAssetLibrary.load_asset(str(report.path))
                save_fixed = False
                for source, results in report.alerts.items():
                    for alert, check in results:
                        if check.is_fixable:
                            try:
                                check.fix(asset, alert, report.props.get(source))
                                fix_result = FixResult(report.name, alert.id, "fixed", source)
                                save_fixed = True
                            except Exception as e:
                                fix_result = FixResult(report.name, alert.id, "failed", source, f"Failed to fix asset. {e}")
                        else:
                            fix_result = FixResult(report.name, alert.id, "skipped", source)
                        fix_results.append(fix_result)

                if save_fixed:
                    unreal.EditorAssetLibrary.save_loaded_asset(asset)

                current_packages = unreal.PackageLoaderManager.get_loaded_package_count()
                if current_packages - len(base_packages) > _PACKAGE_BUDGET:
                    unreal.PackageLoaderManager.unload_loaded_packages(base_packages)
                    unreal.SystemLibrary.collect_garbage()

            except Exception as e:
                unreal.log_error("Failed to fix asset", e)
                for source, results in report.alerts.items():
                    for alert, check in results:
                        fix_result = FixResult(report.name, alert.id, "failed", source, str(e))
                        fix_results.append(fix_result)

    unreal.PackageLoaderManager.unload_loaded_packages(base_packages)
    unreal.SystemLibrary.collect_garbage()
    return fix_results
