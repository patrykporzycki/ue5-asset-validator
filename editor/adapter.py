import unreal

def get_texture_properties (texture: unreal.Texture2D):
    texture_properties = {
        "name": str(texture.get_fname()),
        "resolution_x": texture.blueprint_get_size_x(),
        "resolution_y": texture.blueprint_get_size_y(),
        "compression": texture.get_editor_property("compression_settings").name,
        "srgb": texture.get_editor_property("srgb"),
        "mip_gen": texture.get_editor_property("mip_gen_settings").name
    }
    return texture_properties