import unreal
import pathlib

from core.texture_checker import check_power_of_two, check_max_resolution, check_mipmaps, check_srgb, check_compression, set_suffix_rules
from editor.adapter import get_texture_properties
from editor.fixer import fix_mipmaps, fix_power_of_two, fix_max_resolution, fix_srgb, fix_compression
from core.rule_loader import load_rules

def run(config_path = None):

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
        texture_resolution_x = properties['resolution_x']
        texture_resolution_y = properties['resolution_y']

        texture_checks = [
            (check_power_of_two, [properties['resolution_x'], properties['resolution_y']]),
            (check_max_resolution, [properties['resolution_x'], properties['resolution_y'], rules["max_resolution"]]),
            (check_mipmaps, [properties['mipmaps']]),
            (check_srgb, [properties['srgb'], properties['name']]),
            (check_compression, [properties['compression'], properties['name']]),
        ]

        texture_has_problems = False
        for texture_check, texture_properties in texture_checks:
            result = texture_check(*texture_properties)
            if result is not None:
                texture_has_problems = True
                unreal.log(f"{texture_name}: {result.message}")
                if result.id == "mipmaps":
                    fix_mipmaps(texture)
                elif result.id == "power_of_two":
                    fix_power_of_two(texture)
                elif result.id == "max_resolution":
                    fix_max_resolution(texture, rules["max_resolution"])
                    unreal.log(f"Previous resolution: {texture_resolution_x}x{texture_resolution_y}")
                elif result.id == "srgb":
                    fix_srgb(texture, result.correct_value)
                elif result.id == "compression":
                    fix_compression(texture, result.correct_value)
        if not texture_has_problems:
            unreal.log(f"{texture_name}: OK")


        

