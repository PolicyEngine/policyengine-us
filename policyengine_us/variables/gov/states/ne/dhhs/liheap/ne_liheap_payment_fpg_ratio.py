from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ne_liheap_payment_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = "/1"
    label = "Nebraska LIHEAP payment income as a share of the federal poverty guideline"
    defined_for = StateCode.NE
    # PDF pages 2-3
    reference = "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap
        gross = spm_unit("ne_liheap_gross_income", period)
        earned = spm_unit("ne_liheap_earned_income", period)
        income = max_(gross - earned * p.earned_income_disregard, 0)
        size = spm_unit("ne_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # The heating and cooling payment bands stop growing at six people;
        # eligibility does not. The Guidance footnotes state the size-6+ tier
        # cutoffs in "gross countable income", while the same pages base every
        # payment on "income after the disregard is applied" with no size
        # exception; the disregard is applied at every size here.
        payment_fpg = fpg(
            clip(size, 1, p.payment_size_limit),
            state_group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        return income / payment_fpg
