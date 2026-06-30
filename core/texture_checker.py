from core.alert import Alert

_SUFFIX_RULES = {}


def set_suffix_rules(rules: dict):
    _SUFFIX_RULES.update(rules)


def _is_power_of_two(n: int) -> bool:
    # TODO: check if texture dimensions from UE5 are always positive integers
    return (n & (n - 1)) == 0


def check_power_of_two(resolution_x: int, resolution_y: int) -> Alert | None:
    if _is_power_of_two(resolution_x) and _is_power_of_two(resolution_y):
        return None
    return Alert(
            id="power_of_two",
            severity="warning",
            message=f"Resolution {resolution_x}x{resolution_y} is not a power of two!",
            current_value=f"{resolution_x}x{resolution_y}",
            correct_value=None
        )

def check_max_resolution(resolution_x: int, resolution_y: int, max_resolution: int) -> Alert | None:
    current_resolution = max(resolution_x, resolution_y)
    if current_resolution > max_resolution:
        return Alert(
            id="max_resolution",
            severity="warning",
            message=f"Resolution {resolution_x}x{resolution_y} exceeds {max_resolution}!",
            current_value=str(current_resolution),
            correct_value=str(max_resolution)
        )
    return None


def check_mipmaps(mipgen_settings: str) -> Alert | None:
    if mipgen_settings == "TMGS_NO_MIPMAPS":
        return Alert(
            id="mipmaps",
            severity="critical",
            message="Mipmaps disabled!",
            current_value="TMGS_NO_MIPMAPS",
            correct_value="TMGS_FROM_TEXTURE_GROUP"
        )
    return None


def _find_rule(texture_name: str) -> dict | None:
    for suffix, rule in _SUFFIX_RULES.items():
        if texture_name.lower().endswith(suffix):
            return rule
    return None


def check_srgb(srgb_settings: bool, texture_name: str) -> Alert | None:
    rule = _find_rule(texture_name)
    if rule is None:
        return None
    if srgb_settings != rule['srgb']:
        return Alert(
            id="srgb",
            severity="warning",
            message=f"sRGB setting is set to {srgb_settings}, but texture name suggests {rule['srgb']}",
            current_value=srgb_settings,
            correct_value=rule['srgb'],
        )
    return None


def check_compression(compression_settings: str, texture_name: str) -> Alert | None:
    rule = _find_rule(texture_name)
    if rule is None:
        return None
    if compression_settings != rule['compression']:
        return Alert(
            id="compression",
            severity="warning",
            message=f"Compression setting is set to {compression_settings}, but texture name suggests {rule['compression']}",
            current_value=compression_settings,
            correct_value=rule['compression'],
        )
    return None
