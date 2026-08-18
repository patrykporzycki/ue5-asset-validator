from core.types import Check
from core.types import Alert, Severity

# ENiagaraEmitterCalculateBoundMode (UE 5.7):
# 0 = Dynamic, 1 = Fixed, 2 = Programmable (bounds set at runtime via data interface/BP)
BOUND_MODE_DYNAMIC = 0


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
            if emitter.b_gpu_sim and emitter.bounds_mode == BOUND_MODE_DYNAMIC:
                alerts.append(Alert(
                    id="gpu_dynamic_bounds",
                    severity=Severity.WARNING,
                    message=f"GPU emitter '{emitter.emitter_name}' — Dynamic bounds may be incorrect!",
                    current_value="Dynamic bounds",
                    correct_value="Fixed bounds",
                ))
        return alerts


NIAGARA_CHECKS = [
    InactiveEmittersCheck(),
    GpuDynamicBoundsCheck(),
]
