from policyengine_us.model_api import *


class hi_liheap_subsidized_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP flat heating benefit for subsidized dwellings"
    definition_period = YEAR
    unit = USD
    defined_for = "hi_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=10",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        p = parameters(period).gov.states.hi.dhs.liheap.payment
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # This output covers subsidized dwellings only. Private dwellings receive
        # points times a statewide value per point, which was not located for
        # FY2026, so zero here is not a private dwelling's entitlement. The same
        # schedule pays net-consuming photovoltaic households, whose production
        # has no input.
        return where(subsidized, p.subsidized_amount.calc(size), 0)
