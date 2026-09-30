from policyengine_us.model_api import *


class ms_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Mississippi LIHEAP regular heating eligibility"
    defined_for = StateCode.MS
    reference = "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=22,23,24,29,30,31,32,33"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        income = spm_unit("ms_liheap_income", period)
        limit = spm_unit("ms_liheap_income_limit", period)
        has_adult = spm_unit.any(spm_unit.members("age", period) >= p.adult_age)
        # Existing inputs do not establish emancipated-minor headship, institutional
        # residence, or utility account ownership. A household adult is the modeled
        # applicant; children can establish immigration eligibility under Rule 6.3.
        responsible = (spm_unit("heating_expense", period) > 0) | spm_unit(
            "heat_expense_included_in_rent", period
        )
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # Subsidized housing needs separately billed energy (FY2026 plan Section 2).
        housing_eligible = ~subsidized | ~spm_unit(
            "heat_expense_included_in_rent", period
        )
        return (
            (size > 0) & (income <= limit) & has_adult & responsible & housing_eligible
        )
