from policyengine_us.model_api import *


class mi_ccap_authorized_hours(Variable):
    value_type = float
    entity = SPMUnit
    unit = "hour"
    definition_period = MONTH
    defined_for = StateCode.MI
    label = "Michigan CDC authorized hours per two-week pay period"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EXF/BP/Public/BEM/710.pdf#page=1"
    )

    def formula(spm_unit, period, parameters):
        # BEM 710: biweekly need hours = activity hours over the two-week pay
        # period. We don't track meal periods, study/lab time, or travel
        # add-ons at the moment, so we use base activity hours only. We use
        # hours before labor supply responses to avoid a circular dependency
        # with the labor supply model.
        p = parameters(period).gov.states.mi.mdhhs.ccap
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        weekly_hours = person("weekly_hours_worked_before_lsr", period.this_year)
        biweekly_hours = weekly_hours * 2
        # BEM 710 p.2: for two-parent households, authorize on the parent with
        # the highest need hours (effective 2024-11-03). Non-P/SP members get
        # zero so they never raise the authorized hours.
        head_spouse_hours = where(is_head_or_spouse, biweekly_hours, 0)
        if p.two_parent_uses_highest_hours:
            need_hours = spm_unit.max(head_spouse_hours)
        else:  # noqa
            # Prior rule (before 2024-11-03): authorize on the fewest hours.
            need_hours = spm_unit.min(where(is_head_or_spouse, biweekly_hours, np.inf))
        return p.authorized_hours.tiers.calc(need_hours)
