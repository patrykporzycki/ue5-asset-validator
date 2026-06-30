from dataclasses import dataclass

@dataclass
class Alert:
    id : str
    severity: str
    message: str
    current_value: str | bool
    correct_value: str | bool | None

