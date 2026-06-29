import unreal

from core.texture_checker import check_power_of_two, check_max_resolution, check_mipmaps, check_srgb, check_compression
from editor.adapter import get_texture_properties
from editor.fixer import fix_mipmaps, fix_srgb

def run():

    selection = unreal.EditorUtilityLibrary.get_selected_assets()
    textures = [a for a in selection if isinstance(a, unreal.Texture2D)]

    if not textures:
        unreal.log("No textures selected!")
        return

    unreal.log(f"Checking {len(textures)} textures...")
    for texture in textures:
        properties = get_texture_properties(texture)
        texture_name = properties['name']

        texture_checks = [
            (check_power_of_two, [properties['resolution_x'], properties['resolution_y']]),
            (check_max_resolution, [properties['resolution_x'], properties['resolution_y'], 2048]),
            (check_mipmaps, [properties['mip_gen']]),
            (check_srgb, [properties['srgb'], properties['name']]),
            (check_compression, [properties['compression'], properties['name']]),
        ]

        texture_has_problems = False
        for texture_check, texture_properties in texture_checks:
            result = texture_check(*texture_properties)
            if result is not None:
                texture_has_problems = True
                unreal.log(f"{texture_name}: {result}")
                if texture_check is check_mipmaps:
                    fix_mipmaps(texture)

        if not texture_has_problems:
            unreal.log(f"{texture_name}: Ok")


        

