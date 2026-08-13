def resolve_config(check_id: str, asset_path: str, rules: dict, on_import: bool = False) -> dict | None:

    defaults = rules.get("defaults", {}).get("checks", {}).get(check_id)
    if defaults is None:
        return None

    config = dict(defaults)
    config["params"] = dict(defaults.get("params", {}))

    for preset in rules.get("presets", []):
        for folder in preset.get("folders", []):
            if folder in asset_path:
                overrides = preset.get("overrides", {}).get("checks", {}).get(check_id, {})
                config.update({k: v for k, v in overrides.items() if k != "params"})
                if "params" in overrides:
                    config["params"].update(overrides["params"])
                break

    if not config.get("enabled", False):
        return None

    if on_import and not config.get("run_on_import", True):
        return None

    return config