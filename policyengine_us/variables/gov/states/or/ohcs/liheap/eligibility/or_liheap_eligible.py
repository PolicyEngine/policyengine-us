from policyengine_us.model_api import *


class or_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP regular heating eligibility"
    defined_for = StateCode.OR
    # Manual PDF pages 11, 30, 36, 61, 77, 93, 94; OAR 813-200-0020(1)(b).
    reference = (
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=61",
        "https://www.law.cornell.edu/regulations/oregon/Or-Admin-Code-SS-813-200-0020",
    )
    documentation = (
        "SPM members approximate the economic household, with identity and SSN "
        "verification assumed complete. The energy burden test follows OAR "
        "813-200-0020(1)(b) and the manual's energy burden table: subsidized housing "
        "with heat included in rent is excluded even when the household pays a "
        "separate non-heating utility bill. The Oregon sources do not prescribe a "
        "SNAP immigration test. No asset or categorical income test applies. "
        "Institutional residence, tribal duplicate awards, documentation and "
        "application timing are not modeled. A zero benefit above size 12 or for an "
        "unknown county denotes unsupported schedule coverage, not a legal denial."
    )

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        heating_cost = spm_unit("has_heating_expense", period) | heat_in_rent
        income = spm_unit("or_liheap_countable_income", period)
        return (
            heating_cost
            & ~(heat_in_rent & subsidized)
            & (income <= spm_unit("or_liheap_income_limit", period))
        )
