from dataclasses import dataclass, field

import unreal
from core.types import AssetAdapter, BaseProps


@dataclass
class EmitterBoundsInfo:
    emitter_name: str = ""
    b_gpu_sim: bool = False
    b_local_space: bool = False
    bounds_mode: int = 0
    emitter_fixed_bounds_size: float = 0.0
    b_determinism: bool = False
    num_enabled_light_renderers: int = 0
    b_enabled: bool = False
    b_fixed_bounds: bool = False
    num_enabled_renderers: int = 0


@dataclass
class NiagaraProps(BaseProps):
    emitters: int = 0
    active_emitters: int = 0
    emitter_bounds: list = field(default_factory=list)
    effect_type: str = ""
    b_system_determinism: bool = False
    b_fixed_bounds: bool = False


class NiagaraAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None) -> NiagaraProps:
        props = NiagaraProps(
            name=str(asset_data.asset_name),
            path=str(asset_data.package_name),
            emitters=int(self.get_tag(asset_data, "NumEmitters") or 0),
            active_emitters=int(self.get_tag(asset_data, "ActiveEmitters") or 0),
        )
        if asset:
            try:
                emitters_data = unreal.NiagaraPropsHelper.get_niagara_emitters_data(asset)
                effect_type_object = asset.get_editor_property("effect_type")
                props.effect_type = effect_type_object.get_name() if effect_type_object else ""
                props.b_system_determinism = bool(asset.get_editor_property("determinism"))
                props.b_fixed_bounds = bool(emitters_data[0].fixed_bounds) if emitters_data else False
                props.emitter_bounds = [
                    EmitterBoundsInfo(
                        emitter_name=str(e.emitter_name),
                        b_gpu_sim=bool(e.gpu_sim),
                        b_local_space=bool(e.local_space),
                        bounds_mode=int(e.bounds_mode),
                        emitter_fixed_bounds_size=float(e.emitter_fixed_bounds_size),
                        b_determinism=bool(e.determinism),
                        num_enabled_light_renderers=int(e.num_enabled_light_renderers),
                        b_enabled=bool(e.enabled),
                        b_fixed_bounds=bool(e.fixed_bounds),
                        num_enabled_renderers=int(e.num_enabled_renderers),
                    )
                    for e in emitters_data
                ]
            except Exception as exc:
                unreal.log_warning(f"NiagaraPropsHelper failed for {props.path}: {exc}")
        return props
