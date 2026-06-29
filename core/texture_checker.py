_SUFFIX_RULES = {
    "_n": {"srgb": False, "compression": "TC_NORMALMAP"},
    "_normal": {"srgb": False, "compression": "TC_NORMALMAP"},
    "_nrm": {"srgb": False, "compression": "TC_NORMALMAP"},

    "_r": {"srgb": False, "compression": "TC_GRAYSCALE"},
    "_roughness": {"srgb": False, "compression": "TC_GRAYSCALE"},

    "_m": {"srgb": False, "compression": "TC_GRAYSCALE"},
    "_metallic": {"srgb": False, "compression": "TC_GRAYSCALE"},

    "_ao": {"srgb": False, "compression": "TC_GRAYSCALE"},
    "_ambientocclusion": {"srgb": False, "compression": "TC_GRAYSCALE"},
    "_ambient_occlusion": {"srgb": False, "compression": "TC_GRAYSCALE"},

    "_orm": {"srgb": False, "compression": "TC_MASKS"},
    "_arm": {"srgb": False, "compression": "TC_MASKS"},

    "_masks": {"srgb": False, "compression": "TC_MASKS"},
    "_mask": {"srgb": False, "compression": "TC_MASKS"},

    "_d": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_diffuse": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_albedo": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_basecolor": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_base_color": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_col": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_color": {"srgb": True, "compression": "TC_BASECOLOR"},

    "_spec": {"srgb": False, "compression": "TC_GRAYSCALE"},
    "_specular": {"srgb": False, "compression": "TC_GRAYSCALE"},

    "_opacity": {"srgb": False, "compression": "TC_GRAYSCALE"},
    "_alpha": {"srgb": False, "compression": "TC_GRAYSCALE"},

    "_e": {"srgb": True, "compression": "TC_BASECOLOR"},
    "_emissive": {"srgb": True, "compression": "TC_BASECOLOR"},

    "_h": {"srgb": False, "compression": "TC_DISPLACEMENT"},
    "_height": {"srgb": False, "compression": "TC_DISPLACEMENT"},
    "_disp": {"srgb": False, "compression": "TC_DISPLACEMENT"},
    "_displacement": {"srgb": False, "compression": "TC_DISPLACEMENT"},
}

def _is_power_of_two(n: int) -> bool:
    # TODO: check if texture dimensions from UE5 are always positive integers
    return (n & (n - 1)) == 0

def check_power_of_two(resolution_x: int, resolution_y: int) -> str | None:
    if _is_power_of_two(resolution_x) and _is_power_of_two(resolution_y):
        return None
    return f"Resolution {resolution_x}x{resolution_y} is not a power of two!"

def check_max_resolution(resolution_x:int, resolution_y: int, max_resolution: int) -> str | None:
    if max(resolution_x, resolution_y) > max_resolution:
        return f"Resolution {resolution_x}x{resolution_y} exceeds {max_resolution}!"
    return None

def check_mipmaps(mipgen_settings: str) -> str | None:
    if mipgen_settings == "TMGS_NO_MIPMAPS":
        return "Mipmaps disabled!"
    return None

def _find_rule(texture_name: str) -> dict | None:
    for suffix, rule in _SUFFIX_RULES.items():
        if texture_name.lower().endswith(suffix):
            return rule
    return None

def check_srgb(srgb_settings: bool, texture_name: str) -> str | None:
    rule = _find_rule(texture_name)
    if rule is None:
        return None
    if srgb_settings != rule['srgb']:
        return f"sRGB setting is set to {srgb_settings}, but texture name suggests {rule['srgb']}"
    return None

def check_compression(compression_settings: str, texture_name: str) -> str | None:
    rule = _find_rule(texture_name)
    if rule is None:
        return None
    if compression_settings != rule['compression']:
        return f"Compression setting is set to {compression_settings}, but texture name suggests {rule['compression']}"
    return None
