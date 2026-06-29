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
