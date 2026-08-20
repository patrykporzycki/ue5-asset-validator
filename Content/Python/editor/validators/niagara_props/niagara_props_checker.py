from core.types import Check
from core.types import Alert, Severity


class InactiveEmittersCheck(Check):
    check_id = "inactive_emitters"

    def check(self, props, config) -> list[Alert]:
        if props.emitters > props.active_emitters:
            return [Alert(
                id="inactive_emitters",
                severity=Severity.INFO,
                message=f"Asset has {props.emitters - props.active_emitters} inactive emitter(s)!",
                current_value=str(props.active_emitters),
                correct_value=str(props.emitters),
            )]
        return []


class GpuDynamicBoundsCheck(Check):
    check_id = "gpu_dynamic_bounds"

    def check(self, props, config) -> list[Alert]:
        alerts = []
        for emitter in props.emitter_bounds:
            if emitter.b_gpu_sim and emitter.bounds_mode == 0:
                alerts.append(Alert(
                    id="gpu_dynamic_bounds",
                    severity=Severity.WARNING,
                    message=f"GPU emitter '{emitter.emitter_name}', dynamic bounds may be incorrect!",
                    current_value=emitter.bounds_mode,
                ))
        return alerts


class MissingEffectTypeCheck(Check):
    check_id = "missing_effect_type"

    def check(self, props, config) -> list[Alert]:
        if props.effect_type:
            return []
        return [Alert(
            id="missing_effect_type",
            severity=Severity.INFO,
            message="No EffectType assigned - no Significance Handler / system-level scalability!",
            current_value=props.effect_type or "None",
        )]


class DeterminismMismatchCheck(Check):
    check_id = "determinism_mismatch"

    def check(self, props, config) -> list[Alert]:
        if not props.b_system_determinism:
            return []
        non_deterministic_emitters = [emitter.emitter_name for emitter in props.emitter_bounds if not emitter.b_determinism]
        if not non_deterministic_emitters:
            return []
        return [Alert(
            id="determinism_mismatch",
            severity=Severity.INFO,
            message=f"System is deterministic but emitter(s) are not: {', '.join(non_deterministic_emitters)}",
            current_value=non_deterministic_emitters,
        )]


NIAGARA_CHECKS = [
    InactiveEmittersCheck(),
    GpuDynamicBoundsCheck(),
    MissingEffectTypeCheck(),
    DeterminismMismatchCheck(),
]
