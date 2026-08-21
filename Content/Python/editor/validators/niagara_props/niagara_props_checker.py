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
        if props.b_fixed_bounds:
            return []
        alerts = []
        for emitter in props.emitter_bounds:
            if not emitter.b_gpu_sim:
                continue
            if emitter.bounds_mode == 0:
                alerts.append(Alert(
                    id="gpu_dynamic_bounds",
                    severity=Severity.WARNING,
                    message=f"GPU emitter '{emitter.emitter_name}' uses dynamic bounds - invalid on GPU, set fixed bounds!",
                    current_value=emitter.bounds_mode,
                ))
            elif emitter.bounds_mode == 1 and emitter.emitter_fixed_bounds_size <= 0.0:
                alerts.append(Alert(
                    id="gpu_dynamic_bounds",
                    severity=Severity.WARNING,
                    message=f"GPU emitter '{emitter.emitter_name}' is in fixed bounds mode but has no valid bounds box!",
                    current_value=emitter.emitter_fixed_bounds_size,
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
            message="No EffectType assigned - skipped by Significance Manager (no distance culling/scaling)!",
            current_value=props.effect_type or "None",
        )]


class UseLightRendererCheck(Check):
    check_id = "use_light_renderer"

    def check(self, props, config) -> list[Alert]:
        max_light_renderers = config.get("params", {}).get("max_light_renderers", 0)
        alerts = []
        for emitter in props.emitter_bounds:
            if emitter.num_enabled_light_renderers <= 0:
                continue
            if emitter.b_gpu_sim:
                alerts.append(Alert(
                    id="use_light_renderer",
                    severity=Severity.WARNING,
                    message=f"Emitter '{emitter.emitter_name}' has a light renderer on GPU sim - light renderer is CPU-only and will be ignored!",
                    current_value=emitter.num_enabled_light_renderers,
                ))
            if emitter.num_enabled_light_renderers > max_light_renderers:
                alerts.append(Alert(
                    id="use_light_renderer",
                    severity=Severity.WARNING,
                    message=f"Emitter '{emitter.emitter_name}' uses light renderer - one dynamic light per particle, CPU-only (max allowed: {max_light_renderers})!",
                    current_value=emitter.num_enabled_light_renderers,
                    correct_value=max_light_renderers,
                ))
        return alerts


class InvisibleEmitterCheck(Check):
    check_id = "invisible_emitter"

    def check(self, props, config) -> list[Alert]:
        alerts = []
        for emitter in props.emitter_bounds:
            if emitter.b_enabled and emitter.num_enabled_renderers == 0:
                alerts.append(Alert(
                    id="invisible_emitter",
                    severity=Severity.INFO,
                    message=f"Emitter '{emitter.emitter_name}' is enabled but has no enabled renderer - simulates without rendering!",
                    current_value=emitter.num_enabled_renderers,
                ))
        return alerts


NIAGARA_CHECKS = [
    InactiveEmittersCheck(),
    GpuDynamicBoundsCheck(),
    MissingEffectTypeCheck(),
    UseLightRendererCheck(),
    InvisibleEmitterCheck(),
]
