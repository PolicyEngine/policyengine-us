from policyengine_us.model_api import *


class ne_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP regular heating assistance eligibility"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/rules?agencyId=37&titleId=231",
        "https://dhhs.ne.gov/Documents/LIHEAP%20State%20Plan.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ne_liheap_income_eligible", period)
        # 476 NAC 1-004.09 includes energy paid through rent; FY2026 plan 2.3
        # allows such renters when responsible for a portion of heating costs.
        # Modeling assumption: economic vulnerability under 1-004.06 and
        # 2-002(A) is assumed, rather than separately verified. Market-rate
        # renters with heating paid through rent are accepted even when the
        # separately reported expense is zero. Plan 2.3 requires subsidized
        # housing households to be responsible for a portion of the heating
        # payment, so households receiving housing assistance or living in
        # public housing need a positive heating expense.
        # Administrative disqualifications remain unmodeled.
        has_heating_expense = spm_unit("heating_expense", period) > 0
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        housing_assisted = spm_unit("receives_housing_assistance", period)
        public_housing = spm_unit.household("is_in_public_housing", period)
        subsidized = housing_assisted | public_housing
        responsible = has_heating_expense | (heat_in_rent & ~subsidized)
        return income_eligible & responsible
