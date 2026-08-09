from editor.validators.texture_props.texture_props_checker import TEXTURE_CHECKS
from editor.validators.texture_props.texture_props_adapter import TextureAdapter
from editor.validators.static_mesh_props.static_mesh_props_adapter import StaticMeshPropsAdapter
from editor.validators.static_mesh_props.static_mesh_props_checker import SM_MESH_PROPS_CHECKS
from editor.validators.naming_convention.naming_convention_checker import NAMING_CONVENTION_CHECKS
from editor.validators.naming_convention.naming_convention_adapter import NamingConventionAdapter
from editor.validators.skeletal_mesh_props.skeletal_mesh_props_adapter import SkeletalMeshPropsAdapter
from editor.validators.skeletal_mesh_props.skeletal_mesh_props_checker import SKELETAL_MESH_PROPS_CHECKS
from editor.validators.references.references_checker import REFERENCES_CHECKS
from editor.validators.references.references_adapter import ReferencesAdapter
from editor.validators.niagara_props.niagara_props_adapter import NiagaraAdapter
from editor.validators.niagara_props.niagara_props_checker import NIAGARA_CHECKS
from editor.validators.animation_props.animation_props_adapter import AnimationPropsAdapter
from editor.validators.material_props.material_props_adapter import MaterialPropsAdapter
from core.types import RegistryEntry

VALIDATOR_REGISTRY = {
    "references": RegistryEntry(
        name="references",
        applies_to=["*"],
        adapter=ReferencesAdapter(),
        checks=REFERENCES_CHECKS,
    ),
    "texture_props": RegistryEntry(
        name="texture_props",
        applies_to=["Texture2D"],
        adapter=TextureAdapter(),
        checks=TEXTURE_CHECKS,
    ),
    "static_mesh_props": RegistryEntry(
        name="static_mesh_props",
        applies_to=["StaticMesh"],
        adapter=StaticMeshPropsAdapter(),
        checks = SM_MESH_PROPS_CHECKS,
    ),
    "naming_convention": RegistryEntry(
        name="naming_convention",
        applies_to=["*"],
        adapter=NamingConventionAdapter(),
        checks=NAMING_CONVENTION_CHECKS,
    ),
    "skeletal_mesh_props": RegistryEntry(
        name="skeletal_mesh_props",
        applies_to=["SkeletalMesh"],
        adapter=SkeletalMeshPropsAdapter(),
        checks=SKELETAL_MESH_PROPS_CHECKS,
    ),
    "niagara_props": RegistryEntry(
        name="niagara_props",
        applies_to=["NiagaraSystem"],
        adapter=NiagaraAdapter(),
        checks=NIAGARA_CHECKS,
    ),
    "animation_props": RegistryEntry(
        name="animation_props",
        applies_to=["AnimSequence"],
        adapter=AnimationPropsAdapter(),
        checks=[],
    ),
    "material_props": RegistryEntry(
        name="material_props",
        applies_to=["Material"],
        adapter=MaterialPropsAdapter(),
        checks=[],
    ),

}
