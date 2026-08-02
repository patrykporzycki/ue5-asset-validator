from __future__ import annotations
from core.types import Check
from core.types import Alert, Severity

try:
    import unreal
except ImportError:
    unreal = None

def _find_rule(texture_name: str, suffix_rules: dict) -> dict | None:
    for suffix, rule in suffix_rules.items():
        if texture_name.lower().endswith(suffix):
            return rule
    return None

def _fix_property(texture: unreal.Texture2D, property_name: str, correct_value, label: str):
    previous_property = texture.get_editor_property(property_name)

    texture.set_editor_property(property_name, correct_value)
    new_property = texture.get_editor_property(property_name)

    unreal.log(f"Fixed {label} on {texture.get_fname()}: {previous_property.name if hasattr(previous_property, 'name') else previous_property} -> {new_property.name if hasattr(new_property, 'name') else new_property}")
    return True

def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0

class PowerOfTwoCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        x, y = props.resolution_x, props.resolution_y
        if _is_power_of_two(x) and _is_power_of_two(y):
            return []
        return [Alert(
            id="power_of_two",
            severity=Severity.WARNING,
            message=f"Resolution {props.resolution_x}x{props.resolution_y} is not a power of two!",
            current_value=f"{props.resolution_x}x{props.resolution_y}",
        )]


class MaxResolutionCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        current_resolution = max(props.resolution_x, props.resolution_y)
        if current_resolution > rules['max_resolution']:
            return [Alert(
                id="max_resolution",
                severity=Severity.WARNING,
                message=f"Resolution {props.resolution_x}x{props.resolution_y} exceeds {rules['max_resolution']}!",
                current_value=str(current_resolution),
                correct_value=rules['max_resolution'],
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, options=None):
        return _fix_property(asset, 'max_texture_size', alert.correct_value, 'max resolution')


class MipmapCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        if props.mipmaps == "TMGS_NO_MIPMAPS":
            return [Alert(
                id="mipmaps",
                severity=Severity.WARNING,
                message="Mipmaps disabled!",
                current_value="TMGS_NO_MIPMAPS",
                correct_value="TMGS_FROM_TEXTURE_GROUP",
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, options=None):
        return _fix_property(asset, "mip_gen_settings", unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP,"mipmaps")


class SrgbCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        rule = _find_rule(props.name, rules['suffix_rules'])
        if rule is None:
            return []
        if props.srgb != rule['srgb']:
            return [Alert(
                id="srgb",
                severity=Severity.WARNING,
                message=f"sRGB setting is set to {props.srgb}, but texture name suggests {rule['srgb']}",
                current_value=str(props.srgb),
                correct_value=rule['srgb'],
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, options=None):
        return _fix_property(asset, "srgb", alert.correct_value, "sRGB")


class CompressionCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        rule = _find_rule(props.name, rules['suffix_rules'])
        if rule is None:
            return []
        if props.compression not in rule['compression']:
            return [Alert(
                id="compression",
                severity=Severity.WARNING,
                message=f"Compression setting is set to {props.compression}, but texture name suggests {rule['compression']}",
                current_value=props.compression,
                correct_value=rule['compression'][0],
                is_fixable=True,
            )]
        return []

    def fix(self, asset, alert, options=None):
        return _fix_property(asset, "compression_settings", getattr(unreal.TextureCompressionSettings, alert.correct_value), "compression")

TEXTURE_CHECKS = [
    PowerOfTwoCheck(),
    MaxResolutionCheck(),
    MipmapCheck(),
    SrgbCheck(),
    CompressionCheck(),
]
