from dataclasses import dataclass

import unreal
from core.types import AssetAdapter, BaseProps


@dataclass
class NiagaraProps(BaseProps):
    emitters: int = 0
    active_emitters: int = 0
    has_gpu_emitter: str = ""
    fixed_bounds_size: float | None = None


class NiagaraAdapter(AssetAdapter):
    requires_u_object = True

    def get_properties(self, asset_data: unreal.AssetData, asset=None):
        fixed_bounds_size = self.get_tag(asset_data, "FixedBoundsSize")
        return NiagaraProps(
            name=str(asset_data.asset_name),
            path=str(asset_data.package_name),
            emitters=int(self.get_tag(asset_data, "NumEmitters") or 0),
            active_emitters=int(self.get_tag(asset_data, "ActiveEmitters") or 0),
            has_gpu_emitter=str(self.get_tag(asset_data, "HasGPUEmitter")),
            fixed_bounds_size=float(fixed_bounds_size) if fixed_bounds_size and fixed_bounds_size != "None" else None,
        )
