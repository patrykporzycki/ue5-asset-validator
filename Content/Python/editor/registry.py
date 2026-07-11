from editor.validators.texture_properties.texture_checker import TEXTURE_CHECKS
from editor.validators.texture_properties.texture_adapter import TextureAdapter
from core.types import RegistryEntry


VALIDATOR_REGISTRY = {
    "texture_properties": RegistryEntry(
        name="texture_properties",
        applies_to=["Texture2D"],
        adapter=TextureAdapter(),
        checks=TEXTURE_CHECKS,
    )}
