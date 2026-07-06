from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_pre_obbba_snap_abawd_work_requirements() -> Reform:
    class reform(Reform):
        def apply(self):
            # The baseline ABAWD formulas branch on this person-level
            # variable between post-HR1 rules and a pre-HR1 (2025-06-01)
            # parameter snapshot. Neutralizing it (bool default: false)
            # restores the pre-OBBBA work requirement in every state,
            # overriding the federal toggle and the CA/HI/AK delayed
            # adoption parameters.
            self.neutralize_variable("is_snap_abawd_hr1_in_effect")

    return reform


def create_pre_obbba_snap_abawd_work_requirements_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_pre_obbba_snap_abawd_work_requirements()

    p = parameters.gov.contrib.snap.pre_obbba_abawd_work_requirements
    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_pre_obbba_snap_abawd_work_requirements()
    return None


pre_obbba_snap_abawd_work_requirements = (
    create_pre_obbba_snap_abawd_work_requirements_reform(None, None, bypass=True)
)
