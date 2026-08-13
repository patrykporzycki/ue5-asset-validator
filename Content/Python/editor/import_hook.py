import pathlib

import unreal

from core.rule_loader import load_rules
from core.types import Severity
from editor.runner import validate_asset

_MAX_VALIDATIONS_PER_TICK = 5

import_hook_state = {
    "slate_tick_handle": None,
    "pending_imports": {},
    "validation_rules": None,
    "is_active": False,
}
def _get_validation_rules():
    if import_hook_state["validation_rules"] is None:
        rules_path = pathlib.Path(__file__).parent.parent / "config" / "validation_rules.json"
        import_hook_state["validation_rules"] = load_rules(str(rules_path))
    return import_hook_state["validation_rules"]

def _queue_imported_object(created_object):
    if created_object is None:
        return
    asset_data = unreal.AssetRegistryHelpers.create_asset_data(created_object)
    package_path = str(asset_data.package_name)
    import_hook_state["pending_imports"][package_path] = {
        "asset_data": asset_data,
        "created_object": created_object,
    }

def _on_asset_post_import(factory, created_object):
    _queue_imported_object(created_object)

def _on_asset_reimport(created_object):
    _queue_imported_object(created_object)

def _process_pending_imports(delta_time):
    pending_imports = import_hook_state["pending_imports"]
    if not pending_imports:
        return

    validated_assets_this_tick = 0
    for package_path in list(pending_imports.keys()):
        if validated_assets_this_tick >= _MAX_VALIDATIONS_PER_TICK:
            break
        queued_import = pending_imports.pop(package_path)
        _validate_imported_asset(queued_import["asset_data"], queued_import["created_object"])
        validated_assets_this_tick += 1


def _validate_imported_asset(asset_data, created_object):
    try:
        validation_rules = _get_validation_rules()
        report = validate_asset(asset_data, validation_rules, asset=created_object, on_import=True)
        if report is None:
            return

        total_alerts = 0
        for source, alerts in report.alerts.items():
            for alert, _ in alerts:
                total_alerts += 1
                message = f"[{source}] {report.name}: {alert.message}"
                if alert.severity in (Severity.ERROR, Severity.CRITICAL):
                    unreal.log_error(message)
                elif alert.severity == Severity.WARNING:
                    unreal.log_warning(message)
                else:
                    unreal.log(message)
        if total_alerts:
            unreal.log_warning(f"[AssetValidator] {report.name}: {total_alerts} issue(s) found on import")
    except Exception as e:
        unreal.log_error(f"[AssetValidator] validation failed for {asset_data.package_name}: {e}")


def start_import_hook():
    if import_hook_state["is_active"]:
        return
    import_subsystem = unreal.get_editor_subsystem(unreal.ImportSubsystem)
    import_subsystem.on_asset_post_import.add_callable(_on_asset_post_import)
    import_subsystem.on_asset_reimport.add_callable(_on_asset_reimport)
    import_hook_state["slate_tick_handle"] = unreal.register_slate_post_tick_callback(_process_pending_imports)
    import_hook_state["is_active"] = True
    unreal.log("[AssetValidator] import hook active")


def stop_import_hook():
    if not import_hook_state["is_active"]:
        return
    import_subsystem = unreal.get_editor_subsystem(unreal.ImportSubsystem)
    import_subsystem.on_asset_post_import.remove_callable(_on_asset_post_import)
    import_subsystem.on_asset_reimport.remove_callable(_on_asset_reimport)
    unreal.unregister_slate_post_tick_callback(import_hook_state["slate_tick_handle"])
    import_hook_state["slate_tick_handle"] = None
    import_hook_state["is_active"] = False
    unreal.log("[AssetValidator] import hook stopped")
