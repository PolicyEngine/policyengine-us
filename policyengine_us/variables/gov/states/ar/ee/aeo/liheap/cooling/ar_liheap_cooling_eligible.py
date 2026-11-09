from policyengine_us.model_api import *


class ar_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Arkansas LIHEAP summer regular cooling assistance"
    defined_for = StateCode.AR
    reference = (
        # FY2026 state plan sections 3.1-3.3: the heating income chart and an
        # energy burden; no asset test.
        # PDF pages 12-13
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=12",
        # FFY 2025 manual section 2.1: "Only electric benefits are available
        # during the Summer Program." No FY2026 manual was found.
        "https://liheapch.acf.gov/docs/2025/manuals/AR_Manual_2025.pdf#page=29",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ar_liheap_household_size", period)
        income = spm_unit("ar_liheap_countable_income", period)
        income_limit = spm_unit("ar_liheap_income_limit", period)
        # The summer benefit pays the electric bill, so the energy burden is a
        # cooling cost on the household's own electric account. No input
        # identifies electricity included in rent, so those households are not
        # paid.
        electric_bill = spm_unit("pre_subsidy_electricity_expense", period)
        # No heat and every known fuel can be paid. An unspecified heating fuel
        # pays $0, as in every state LIHEAP program (issue 9754).
        fuel = spm_unit("heating_type", period)
        return (
            (size > 0)
            & (income <= income_limit)
            & spm_unit("has_cooling_expense", period)
            & (electric_bill > 0)
            & (fuel != fuel.possible_values.UNSPECIFIED)
        )
