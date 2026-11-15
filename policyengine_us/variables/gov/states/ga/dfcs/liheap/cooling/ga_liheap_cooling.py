from policyengine_us.model_api import *


class ga_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP regular cooling benefit"
    defined_for = "ga_liheap_cooling_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/GA_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/GA_BenefitMatrix_2025.pdf",
        # FY2026 state plan section 3.6 ($400 to $500) and item 16.1 (no senior
        # maximum).
        # PDF pages 11, 30
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=11",
        # PAMMS chapter 100: one cooling benefit per program year.
        "https://pamms.dhs.ga.gov/dfcs/_exports/liheap.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap
        size = spm_unit("ga_liheap_household_size", period)
        income = spm_unit("ga_liheap_income", period)
        # Step 1 sets the income level as for heating. Step 2 prints one cooling
        # amount per level for every main heating fuel, with no cap at the bill.
        lookup_size = clip(size, 1, p.payment.maximum_table_size)
        lower_income = income <= p.payment.lower_income_limit[lookup_size]
        return where(
            lower_income, p.cooling.amount.lower_income, p.cooling.amount.higher_income
        )
