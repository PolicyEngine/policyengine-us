from policyengine_us.model_api import *


class ma_liheap_eligible_subsidized_housing(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Massachusetts LIHEAP eligible subsidized housing"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://liheapch.acf.gov/tables/subsidize.htm#MA"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap.eligibility
        income = spm_unit("ma_liheap_income", period)
        rent_threshold = income * p.rent_threshold_subsidized_housing
        total_rent = add(spm_unit, period, ["rent"])
        # Eligible if monthly rent is more than a certain fraction of income
        rent_eligible = total_rent > rent_threshold
        is_subsidized = spm_unit("receives_housing_assistance", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)

        return (is_subsidized & heat_in_rent & rent_eligible) | (
            is_subsidized & ~heat_in_rent
        )
