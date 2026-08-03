from __future__ import annotations
from core.types import Check, FixOption
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

def _prev_pot(n):
    p = 1
    while p <= n:
        p = p * 2
    return p // 2

class TextureResolutionCheck(Check):

    def check(self, props, rules) -> list[Alert]:
        x, y = props.resolution_x, props.resolution_y
        max_resolution = rules['max_resolution']
        is_power_of_two = _is_power_of_two(x) and _is_power_of_two(y)
        exceeds_max_resolution = max(x,y) > max_resolution
        if is_power_of_two and exceeds_max_resolution:
            return []

        longest = max(x, y)
        cap = min(longest, max_resolution)
        target_long = _prev_pot(cap)

        scale = target_long /longest
        if x >= y:
            target_x, target_y = target_long, _prev_pot(int(y*scale))
        else:
            target_x, target_y = _prev_pot(int(x*scale)), target_long

        alerts = []
        if not is_power_of_two:
            alerts.append(Alert(
                id="power_of_two",
                severity=Severity.ERROR,
                message=f"Resolution {x}x{y} is not a power of two!",
                current_value=[x, y],
                correct_value=[target_x, target_y],
                is_fixable=True,
            ))
        if exceeds_max_resolution:
            alerts.append(Alert(
                id="max_resolution",
                severity=Severity.WARNING,
                message=f"Resolution {x}x{y} exceeds limit of {max_resolution}!",
                current_value=[x, y],
                correct_value=[target_x, target_y],
                is_fixable=True,
            ))
        return alerts

    def fix(self, asset, alert, props=None, options=None):
        if options and options.get('target_resolution'):
            target_x, target_y = options['target_resolution']
        else:
            target_x, target_y = alert.correct_value
        return unreal.TexturePropsHelper.fix_power_of_two(asset, target_x, target_y)

    def get_fix_options(self, alert, props, rules):
        x, y = props.resolution_x, props.resolution_y
        target_x, target_y = alert.correct_value
        max_resolution = max(target_x, target_y)

        longest = max(x, y)
        choices = []
        p = _prev_pot(max_resolution//5)
        while p <= max_resolution:
            scale = p / longest
            cx = _prev_pot(int(x * scale))
            cy = _prev_pot(int(y * scale))
            choices.append((cx, cy))
            p = p * 2

        return [FixOption(
            key="target_resolution",
            label="Target Resolution",
            default=(target_x, target_y),
            choices=tuple(choices),
        )]

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

    def fix(self, asset, alert, props=None, options=None):
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

    def fix(self, asset, alert, props = None, options=None):
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

    def fix(self, asset, alert, props = None, options=None):
        return _fix_property(asset, "compression_settings", getattr(unreal.TextureCompressionSettings, alert.correct_value), "compression")

TEXTURE_CHECKS = [
    TextureResolutionCheck(),
    MipmapCheck(),
    SrgbCheck(),
    CompressionCheck(),
]
