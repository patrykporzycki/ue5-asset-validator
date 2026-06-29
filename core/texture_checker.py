_SUFFIX_RULES = {}

def set_suffix_rules(rules: dict):
    _SUFFIX_RULES.update(rules)

def _is_power_of_two(n: int) -> bool:
    # TODO: check if texture dimensions from UE5 are always positive integers
    return (n & (n - 1)) == 0

def check_power_of_two(resolution_x: int, resolution_y: int) -> str | None:
    if _is_power_of_two(resolution_x) and _is_power_of_two(resolution_y):
        return None
    return f"Resolution {resolution_x}x{resolution_y} is not a power of two!"

def check_max_resolution(resolution_x:int, resolution_y: int, max_resolution: int) -> str | None:
    if max(resolution_x, resolution_y) > max_resolution:
        return f"Resolution {resolution_x}x{resolution_y} exceeds {max_resolution}!"
    return None

def check_mipmaps(mipgen_settings: str) -> str | None:
    if mipgen_settings == "TMGS_NO_MIPMAPS":
        return "Mipmaps disabled!"
    return None

def _find_rule(texture_name: str) -> dict | None:
    for suffix, rule in _SUFFIX_RULES.items():
        if texture_name.lower().endswith(suffix):
            return rule
    return None

def check_srgb(srgb_settings: bool, texture_name: str) -> str | None:
    rule = _find_rule(texture_name)
    if rule is None:
        return None
    if srgb_settings != rule['srgb']:
        return f"sRGB setting is set to {srgb_settings}, but texture name suggests {rule['srgb']}"
    return None

def check_compression(compression_settings: str, texture_name: str) -> str | None:
    rule = _find_rule(texture_name)
    if rule is None:
        return None
    if compression_settings != rule['compression']:
        return f"Compression setting is set to {compression_settings}, but texture name suggests {rule['compression']}"
    return None
