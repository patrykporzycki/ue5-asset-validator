import unreal
from core.types import AssetAdapter

class NiagaraAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        fixed_bounds_size = self.get_tag(asset_data, "FixedBoundsSize")
        asset_properties = {
            "name": str(asset_data.asset_name),
            "emitters": int(self.get_tag(asset_data, "NumEmitters") or 0),
            "active_emitters": int(self.get_tag(asset_data, "ActiveEmitters") or 0),
            "has_gpu_emitter": str(self.get_tag(asset_data, "HasGPUEmitter")),
            "fixed_bounds_size": float(fixed_bounds_size) if fixed_bounds_size and fixed_bounds_size != "None" else None,
            "estimated_size": 250,
        }
        return asset_properties