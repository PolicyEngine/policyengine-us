from policyengine_us.model_api import *


class ct_tfa_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=53",
        "https://secure.ssa.gov/poms.nsf/lnx/0500830403BOS",
    )
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment

        if p.regional_in_effect:
            size = spm_unit("spm_unit_size", period.this_year)
            capped_size = min_(size, p.max_unit_size)
            region = spm_unit.household("ct_tfa_region", period)
            region_a = region == region.possible_values.REGION_A
            region_c = region == region.possible_values.REGION_C
            return select(
                [region_a, region_c],
                [
                    p.regional.region_a.amount[capped_size],
                    p.regional.region_c.amount[capped_size],
                ],
                default=p.regional.region_b.amount[capped_size],
            )

        need_standard = spm_unit("ct_tfa_need_standard", period)
        return p.payment_standard_rate * need_standard
