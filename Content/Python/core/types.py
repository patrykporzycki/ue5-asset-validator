from dataclasses import dataclass

@dataclass
class Alert:
    id : str
    severity: str
    message: str
    current_value: str
    correct_value: str | bool | int | None

@dataclass
class Report:
    path: str
    name: str
    type: str
    estimated_size: int
    alerts: list[Alert]

@dataclass
class FixResult:
    name: str
    alert: str
    status: str
    error: str | None = None




