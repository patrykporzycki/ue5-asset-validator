from editor.validators.texture_properties.texture_checker import TEXTURE_CHECKS
from editor.validators.texture_properties.texture_adapter import TextureAdapter
from editor.validators.static_mesh_properties.static_mesh_adapter import StaticMeshAdapter
from editor.validators.static_mesh_properties.static_mesh_checker import STATIC_MESH_CHECKS
from editor.validators.naming_convention.naming_convention_checker import NAMING_CONVENTION_CHECKS
from editor.validators.naming_convention.naming_convention_adapter import NamingConventionAdapter
from editor.validators.skeletal_mesh_properties.skeletal_mesh_adapter import SkeletalMeshAdapter
from editor.validators.skeletal_mesh_properties.skeletal_mesh_checker import SKELETAL_MESH_CHECKS
from editor.validators.references.references_checker import REFERENCES_CHECKS
from editor.validators.references.references_adapter import ReferencesAdapter
from editor.validators.niagara_properties.niagara_properties_adapter import NiagaraAdapter
from editor.validators.niagara_properties.niagara_properties_checker import NIAGARA_CHECKS
from editor.validators.animation_properties.animation_properties_adapter import AnimationPropertiesAdapter

from core.types import RegistryEntry

VALIDATOR_REGISTRY = {
    "references": RegistryEntry(
        name="references",
        applies_to=["*"],
        adapter=ReferencesAdapter(),
        checks=REFERENCES_CHECKS,
    ),
    "texture_properties": RegistryEntry(
        name="texture_properties",
        applies_to=["Texture2D"],
        adapter=TextureAdapter(),
        checks=TEXTURE_CHECKS,
    ),
    "static_mesh_properties": RegistryEntry(
        name="static_mesh_properties",
        applies_to=["StaticMesh"],
        adapter=StaticMeshAdapter(),
        checks = STATIC_MESH_CHECKS,
    ),
    "naming_convention": RegistryEntry(
        name="naming_convention",
        applies_to=["*"],
        adapter=NamingConventionAdapter(),
        checks=NAMING_CONVENTION_CHECKS,
    ),
    "skeletal_mesh_properties": RegistryEntry(
        name="skeletal_mesh_properties",
        applies_to=["SkeletalMesh"],
        adapter=SkeletalMeshAdapter(),
        checks=SKELETAL_MESH_CHECKS,
    ),
    "niagara_properties": RegistryEntry(
        name="niagara_properties",
        applies_to=["NiagaraSystem"],
        adapter=NiagaraAdapter(),
        checks=NIAGARA_CHECKS,
    ),
    "animation_properties": RegistryEntry(
        name="animation_properties",
        applies_to=["AnimSequence"],
        adapter=AnimationPropertiesAdapter(),
        checks=[],
    ),
}
