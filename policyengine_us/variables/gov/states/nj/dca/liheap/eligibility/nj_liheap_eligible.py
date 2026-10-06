from policyengine_us.model_api import *


class nj_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP regular heating eligibility"
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 5, 6, 7, 11, 12.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=5",
        # PDF pages 5, 6, 7, 12, 13.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=5",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-2-2",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-2-3",
    )
    documentation = (
        "Automatic enrollment does not waive the income test, and regular heating has "
        "no asset test. Striker and institutional-residence exclusions, full "
        "utility-allowance coverage and payments by people outside the household need "
        "inputs not available here. Unknown county is unsupported, not a legal denial."
    )

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Handbook 2.2 (page 6) and N.J.A.C. 5:49-2.3(b)1-2 deny public housing
        # and rent-subsidy households only when the subsidy covers the heat.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        person = spm_unit.members
        dependent_students_only = spm_unit.all(
            person("is_full_time_student", period)
            & person("is_tax_unit_dependent", period)
        )
        return (
            (spm_unit("has_heating_expense", period) | heat_in_rent)
            & ~(heat_in_rent & subsidized)
            & ~dependent_students_only
            & (spm_unit("nj_liheap_household_size", period) > 0)
            & (
                spm_unit("nj_liheap_countable_income", period)
                <= spm_unit("nj_liheap_income_limit", period)
            )
        )
