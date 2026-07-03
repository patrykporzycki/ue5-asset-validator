import unreal
import pathlib

from core.texture_checker import TEXTURE_CHECKS, set_suffix_rules
from editor.adapter import get_texture_properties
from editor.fixer import fix_mipmaps, fix_power_of_two, fix_max_resolution, fix_srgb, fix_compression
from core.rule_loader import load_rules
from editor.scanner import scan_folders

CHECK_TO_FIXER = {
    "srgb": fix_srgb,
    "compression": fix_compression,
    "mipmaps": fix_mipmaps,
    "max_resolution": fix_max_resolution,
    "power_of_two": fix_power_of_two,
}

def run(config_path = None, asset_paths = None):

    if asset_paths:
        textures = scan_folders(asset_paths)
    else:
        selection = unreal.EditorUtilityLibrary.get_selected_assets()
        textures = [a for a in selection if isinstance(a, unreal.Texture2D)]

    if not textures:
        unreal.log("No textures selected!")
        return

    if config_path is None:
        config_path = pathlib.Path(__file__).parent / "config" / "validation_rules.json"
    rules = load_rules(config_path)
    set_suffix_rules(rules["suffix_rules"])

    unreal.log(f"Checking {len(textures)} textures...")
    for texture in textures:
        properties = get_texture_properties(texture)
        texture_name = properties['name']

        texture_has_problems = False
        for check_name, check_fn in TEXTURE_CHECKS.items():
            alert = check_fn(properties, rules)
            if alert is not None:
                texture_has_problems = True
                unreal.log(f"{texture_name}: {alert.message}")
                CHECK_TO_FIXER[alert.id](texture, alert)
        if not texture_has_problems:
            unreal.log(f"{texture_name}: OK")




