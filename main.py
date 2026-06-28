import unreal
from core.texture_checker import check_power_of_two
from editor.adapter import get_texture_properties

def run():
    selection = unreal.EditorUtilityLibrary.get_selected_assets()
    textures = [a for a in selection if isinstance(a, unreal.Texture2D)]

    if not textures:
        unreal.log("No textures selected!")
        return

    unreal.log(f"Checking {len(textures)} textures...")
    for texture in textures:
        properties = get_texture_properties(texture)
        power_of_two_status = check_power_of_two(properties['resolution_x'], properties['resolution_y'])

        if power_of_two_status is None:
            unreal.log(f"{properties['name']}: OK")
        else:
            unreal.log(f"{properties['name']}: {power_of_two_status}")



        

