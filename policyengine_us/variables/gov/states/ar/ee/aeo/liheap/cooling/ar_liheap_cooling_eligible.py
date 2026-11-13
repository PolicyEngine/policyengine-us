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
        # during the Summer Program." Section 4.8.1: the energy burden of a
        # household that receives a utility bill. No FY2026 manual was found.
        # PDF pages 29, 63
        "https://liheapch.acf.gov/docs/2025/manuals/AR_Manual_2025.pdf#page=29",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ar_liheap_household_size", period)
        income = spm_unit("ar_liheap_countable_income", period)
        income_limit = spm_unit("ar_liheap_income_limit", period)
        # Manual section 4.8.1 finds an energy burden in a utility bill the
        # household receives, and summer pays electric benefits only, so a bill
        # payer needs a positive electric bill. Requiring a cooling cost as
        # well is a PolicyEngine convention with no Arkansas source; it is not
        # part of Arkansas's energy-burden rule.
        pays_electric_bill = spm_unit("has_cooling_expense", period) & (
            spm_unit("pre_subsidy_electricity_expense", period) > 0
        )
        # Plan item 3.3 also makes unsubsidized renters with utilities included
        # in the rent eligible.
        subsidized = spm_unit.household("is_in_public_housing", period) | spm_unit(
            "receives_housing_assistance", period
        )
        utilities_in_rent = ~spm_unit.household("tenant_pays_utilities", period) & (
            add(spm_unit, period, ["rent"]) > 0
        )
        responsible = pays_electric_bill | (utilities_in_rent & ~subsidized)
        return (size > 0) & (income <= income_limit) & responsible
