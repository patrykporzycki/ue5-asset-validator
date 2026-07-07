import unreal
from core.types import Alert

def _fix_property(texture: unreal.Texture2D, property_name: str, correct_value, label: str):
    previous_property = texture.get_editor_property(property_name)
    with unreal.ScopedEditorTransaction(f"Fix {label}"):
        texture.set_editor_property(property_name, correct_value)
    new_property = texture.get_editor_property(property_name)

    unreal.log(f"Fixed {label} on {texture.get_fname()}: {previous_property.name if hasattr(previous_property, 'name') else previous_property} -> {new_property.name if hasattr(new_property, 'name') else new_property}")
    return True

def fix_mipmaps(texture: unreal.Texture2D, alert: Alert):
    return _fix_property(texture, "mip_gen_settings", unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP, "mipmaps")

def fix_srgb(texture: unreal.Texture2D, alert: Alert):
    return _fix_property(texture, "srgb", alert.correct_value, "sRGB")

def fix_compression(texture: unreal.Texture2D, alert: Alert):
    return _fix_property(texture, "compression_settings", getattr(unreal.TextureCompressionSettings, alert.correct_value), "compression")

def fix_max_resolution(texture: unreal.Texture2D, alert: Alert):
    return _fix_property(texture, "max_texture_size", alert.correct_value, "max resolution")
