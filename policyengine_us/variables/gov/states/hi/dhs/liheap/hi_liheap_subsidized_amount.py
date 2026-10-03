from policyengine_us.model_api import *


class hi_liheap_subsidized_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP subsidized dwelling scheduled amount before eligibility"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=10",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        p = parameters(period).gov.states.hi.dhs.liheap.payment
        # This exposes the supported size schedule, not an eligibility award.
        # The same schedule applies to net-consuming photovoltaic households,
        # whose production/use distinction is not a current model input.
        return p.subsidized_amount.calc(size)
