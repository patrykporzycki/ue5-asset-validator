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


@dataclass
class NiagaraProps(BaseProps):
    emitters: int = 0
    active_emitters: int = 0
    emitter_bounds: list = field(default_factory=list)
    effect_type: str = ""


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
                props.effect_type = str(unreal.NiagaraPropsHelper.get_niagara_effect_type_name(asset))
                props.emitter_bounds = [
                    EmitterBoundsInfo(
                        emitter_name=str(e.emitter_name),
                        b_gpu_sim=bool(e.gpu_sim),
                        b_local_space=bool(e.local_space),
                        bounds_mode=int(e.bounds_mode),
                        emitter_fixed_bounds_size=float(e.emitter_fixed_bounds_size),
                    )
                    for e in emitters_data
                ]
            except Exception as exc:
                unreal.log_warning(f"NiagaraPropsHelper failed for {props.path}: {exc}")
        return props
