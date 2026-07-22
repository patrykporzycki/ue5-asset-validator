import unreal
from core.types import AssetAdapter

class AnimationPropertiesAdapter(AssetAdapter):
    def get_properties(self, asset_data: unreal.AssetData):
        fps = float(self.get_tag(asset_data, "Number of Frames") or 1)/float(self.get_tag(asset_data, "SequenceLength") or 1)
        asset_properties = {
            "name": str(asset_data.asset_name),
            "num_frames": float(self.get_tag(asset_data, "Number of Frames") or 0),
            "sequence_length": round(float(self.get_tag(asset_data, "SequenceLength") or 0),2),
            "fps": round(fps,2),
            "bEnableRootMotion": str(self.get_tag(asset_data, "bEnableRootMotion")),
            "retarget_source": str(self.get_tag(asset_data, "RetargetSource")),
            "skeleton": str(self.get_tag(asset_data, "Skeleton")),
            "interpolation": str(self.get_tag(asset_data, "Interpolation")),
            "estimated_size": 500,
        }
        return asset_properties