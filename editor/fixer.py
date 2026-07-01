import unreal

def _fix_property(texture: unreal.Texture2D, property_name: str, correct_value, label: str):
    previous_property = texture.get_editor_property(property_name)
    with unreal.ScopedEditorTransaction(f"Fix {label}"):
        texture.set_editor_property(property_name, correct_value)
    new_property = texture.get_editor_property(property_name)

    unreal.log(f"Fixed {label} on {texture.get_fname()}: {previous_property.name if hasattr(previous_property, 'name') else previous_property} -> {new_property.name if hasattr(new_property, 'name') else new_property}")
    return True

def fix_mipmaps(texture: unreal.Texture2D):
    return _fix_property(texture, "mip_gen_settings", unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP, "mipmaps")

def fix_srgb(texture: unreal.Texture2D, correct_srgb: bool):
    return _fix_property(texture, "srgb", correct_srgb, "sRGB")

def fix_compression(texture: unreal.Texture2D, correct_compression: str):
    return _fix_property(texture, "compression_settings", getattr(unreal.TextureCompressionSettings, correct_compression), "compression")

def fix_power_of_two(texture: unreal.Texture2D):
    return _fix_property(texture, "power_of_two_mode", unreal.TexturePowerOfTwoSetting.PAD_TO_POWER_OF_TWO, "power of two")

def fix_max_resolution(texture: unreal.Texture2D, max_texture_size: int):
    return _fix_property(texture, "max_texture_size", max_texture_size, "max resolution")
