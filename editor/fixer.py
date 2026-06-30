import unreal

def fix_mipmaps(texture: unreal.Texture2D):
    previous_mipmap = texture.get_editor_property("mip_gen_settings").name

    with unreal.ScopedEditorTransaction("Fix Mipmaps"):
        texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
    current_mipmap = texture.get_editor_property("mip_gen_settings").name

    unreal.log(f"Fixed mipmaps on {texture.get_fname()}: {previous_mipmap} -> {current_mipmap}")
    return True

def fix_srgb(texture: unreal.Texture2D, correct_srgb: bool):
    previous_color_space = texture.get_editor_property("srgb")

    with unreal.ScopedEditorTransaction("Fix sRGB"):
        texture.set_editor_property("srgb", correct_srgb)
    current_color_space = texture.get_editor_property("srgb")

    unreal.log(f"Fixed sRGB on {texture.get_fname()}: {previous_color_space} -> {current_color_space}")
    return True

def fix_compression(texture: unreal.Texture2D, correct_compression: str):
    previous_compression = texture.get_editor_property("compression_settings").name

    with unreal.ScopedEditorTransaction("Fix compression"):
        texture.set_editor_property("compression_settings", getattr(unreal.TextureCompressionSettings, correct_compression))
    current_compression = texture.get_editor_property("compression_settings").name

    unreal.log(f"Fixed compression on {texture.get_fname()}: {previous_compression} -> {current_compression}")
    return True

def fix_power_of_two(texture: unreal.Texture2D):
    previous_power_of_two = texture.get_editor_property("power_of_two_mode").name

    with unreal.ScopedEditorTransaction("Fix Power of Two"):
        texture.set_editor_property("power_of_two_mode", unreal.TexturePowerOfTwoSetting.PAD_TO_POWER_OF_TWO)
    current_power_of_two = texture.get_editor_property("power_of_two_mode").name

    unreal.log(f"Fixed power of two mode on {texture.get_fname()}: {previous_power_of_two} -> {current_power_of_two}")
    return True

def fix_max_resolution(texture: unreal.Texture2D, max_texture_size: int, current_resolution_x: int, current_resolution_y: int):
    previous_max_resolution = texture.get_editor_property("max_texture_size")
    current_resolution = f"{current_resolution_x}x{current_resolution_y}"

    with unreal.ScopedEditorTransaction("Fix Max Resolution"):
        texture.set_editor_property("max_texture_size", max_texture_size)
    current_max_resolution = texture.get_editor_property("max_texture_size")

    unreal.log(f"Fixed max resolution on {texture.get_fname()}, dimensions {current_resolution}: {previous_max_resolution} -> {current_max_resolution}")
    return True
