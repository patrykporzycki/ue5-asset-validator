from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AssetAdapter:
    requires_u_object: bool = False

    @staticmethod
    def get_tag(asset_data, tag_name):
        return asset_data.get_tag_value(tag_name)

    def get_properties(self, asset_data, asset=None):
        raise NotImplementedError

@dataclass
class BaseProps:
    name: str
    path: str = ""

@dataclass(frozen=True)
class Alert:
    id : str
    severity: Severity
    message: str
    current_value: Any
    correct_value: Any | None = None
    is_fixable: bool = False

@dataclass(frozen=True)
class FixResult:
    name: str
    alert: str
    status: str
    source: str = ""
    error: str | None = None

@dataclass(frozen=True)
class FixOption:
    key: str
    label: str
    default: Any
    choices: tuple | None = None

class Check:
    check_id: str = ""
    requires_deep: bool = False
    fix_options: list[FixOption] = []

    def is_applicable(self) -> bool:
        return True

    def check(self, properties, rules) -> list[Alert]:
        raise NotImplementedError

    def fix(self, asset, alert, props=None, options:dict|None=None) -> bool:
        return False

    def get_fix_options(self, alert_id, props, rules) -> list[FixOption]:
        return self.fix_options

@dataclass(frozen=True)
class Report:
    path: str
    name: str
    type: str
    alerts: dict[str, list[tuple[Alert, Check]]]
    props: dict
    timestamp: float

@dataclass(frozen=True)
class RegistryEntry:
    name: str
    applies_to: list[str]
    adapter: AssetAdapter
    checks: list
