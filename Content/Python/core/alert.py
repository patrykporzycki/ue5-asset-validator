from dataclasses import dataclass

@dataclass
class Alert:
    id : str
    severity: str
    message: str
    current_value: str
    correct_value: str | None

