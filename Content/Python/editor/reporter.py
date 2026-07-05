import unreal
from editor.adapter import get_asset_properties
from core.types import ReportedAsset
from core.validator import validate

def make_report(asset_datas: unreal.AssetData, rules: dict):
    reports = []
    for asset_data in asset_datas:
        properties = get_asset_properties(asset_data)
        alerts = validate(properties, rules)
        report = ReportedAsset(asset_data.package_name,
                               asset_data.asset_name,
                               asset_data.asset_class_path.asset_name,
                               alerts)
        reports.append(report)
    return reports