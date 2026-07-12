from dataclasses import dataclass
from enum import Enum
import time

class Severity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AssetAdapter:
    @staticmethod
    def get_tag(asset_data, tag_name):
        for _ in range(10):
            val = asset_data.get_tag_value(tag_name)
            if val is not None:
                return val
            time.sleep(0.01)
        return "0"

    def get_properties(self, asset_data):
        raise NotImplementedError

@dataclass(frozen=True)
class Alert:
    id : str
    severity: Severity
    message: str
    current_value: str
    correct_value: str | bool | int | None

@dataclass(frozen=True)
class Report:
    path: str
    name: str
    type: str
    estimated_size: int
    alerts: list[Alert]

@dataclass(frozen=True)
class FixResult:
    name: str
    alert: str
    status: str
    error: str | None = None

@dataclass(frozen=True)
class RegistryEntry:
    name: str
    applies_to: list[str]
    adapter: AssetAdapter
    checks: list

class Check:
    alert_id: str = ""
    severity: Severity = Severity.WARNING

    def __init_subclass__(cls):
        if cls.alert_id == "":
            raise TypeError("Alert ID not provided!")
    def check(self, properties, rules) -> Alert : raise NotImplementedError








