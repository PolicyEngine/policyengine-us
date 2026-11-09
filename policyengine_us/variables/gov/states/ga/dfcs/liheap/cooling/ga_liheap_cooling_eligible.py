from policyengine_us.model_api import *


class ga_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Georgia LIHEAP regular cooling assistance"
    defined_for = StateCode.GA
    reference = (
        # FY2026 state plan sections 3.1-3.3: 60% of state median income, no
        # additional eligibility requirements and no asset test.
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=10",
        # PAMMS chapter 100, export dated 2026-11-04: cooling applicants "must
        # meet the eligibility requirements set forth for the current fiscal
        # year's Heating Program".
        "https://pamms.dhs.ga.gov/dfcs/_exports/liheap.pdf#page=4",
        "https://dfcs.georgia.gov/document/document/liheap-cooling-faq-fy2022/download#page=1",
    )

    def formula(spm_unit, period, parameters):
        # Heating's household size and income tests apply. The energy burden is
        # the household's own cooling cost. No input identifies cooling costs
        # included in rent, so those households are not paid.
        size = spm_unit("ga_liheap_household_size", period)
        # No heat and every known fuel can be paid. An unspecified heating fuel
        # pays $0, as in every state LIHEAP program (issue 9754).
        fuel = spm_unit("heating_type", period)
        return (
            (size > 0)
            & spm_unit("ga_liheap_income_eligible", period)
            & spm_unit("has_cooling_expense", period)
            & (fuel != fuel.possible_values.UNSPECIFIED)
        )
