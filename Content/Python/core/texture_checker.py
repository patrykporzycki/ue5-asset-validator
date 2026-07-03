from core.alert import Alert

_SUFFIX_RULES = {}

def set_suffix_rules(rules: dict):
    _SUFFIX_RULES.update(rules)


def _is_power_of_two(n: int) -> bool:
    return (n & (n - 1)) == 0

def check_power_of_two(props: dict, rules: dict) -> Alert | None:
    if _is_power_of_two(props['resolution_x']) and _is_power_of_two(props['resolution_y']):
        return None
    return Alert(
            id="power_of_two",
            severity="warning",
            message=f"Resolution {props['resolution_x']}x{props['resolution_y']} is not a power of two!",
            current_value=f"{props['resolution_x']}x{props['resolution_y']}",
            correct_value=None
        )


def check_max_resolution(props: dict, rules: dict) -> Alert | None:
    current_resolution = max(props['resolution_x'], props['resolution_y'])
    if current_resolution > rules['max_resolution']:
        return Alert(
            id="max_resolution",
            severity="warning",
            message=f"Resolution {props['resolution_x']}x{props['resolution_y']} exceeds {rules['max_resolution']}!",
            current_value=str(current_resolution),
            correct_value=rules['max_resolution']
        )
    return None


def check_mipmaps(props: dict, rules: dict) -> Alert | None:
    if props['mipmaps'] == "TMGS_NO_MIPMAPS":
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


def check_srgb(props: dict, rules: dict) -> Alert | None:
    rule = _find_rule(props['name'])
    if rule is None:
        return None
    if props['srgb'] != rule['srgb']:
        return Alert(
            id="srgb",
            severity="warning",
            message=f"sRGB setting is set to {props['srgb']}, but texture name suggests {rule['srgb']}",
            current_value=str(props['srgb']),
            correct_value=rule['srgb'],
        )
    return None


def check_compression(props: dict, rules: dict) -> Alert | None:
    rule = _find_rule(props['name'])
    if rule is None:
        return None
    if props['compression'] not in rule['compression']:
        return Alert(
            id="compression",
            severity="warning",
            message=f"Compression setting is set to {props['compression']}, but texture name suggests {rule['compression']}",
            current_value=props['compression'],
            correct_value=rule['compression'][0],
        )
    return None

TEXTURE_CHECKS = {
    "srgb": check_srgb,
    "compression": check_compression,
    "mipmaps": check_mipmaps,
    "max_resolution": check_max_resolution,
    "power_of_two": check_power_of_two,
}