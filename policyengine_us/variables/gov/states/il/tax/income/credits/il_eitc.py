from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.credits.eitc_helpers import (
    calculate_eitc_like_amount,
)


class il_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www2.illinois.gov/rev/programs/EIC/Pages/default.aspx"
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        qualifying_child = person("is_qualifying_child_dependent", period) & has_tin
        child_count = tax_unit.sum(qualifying_child)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        demographic_eligible = (child_count > 0) | tax_unit.any(
            is_head_or_spouse & (age >= 18)
        )
        state_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count,
            demographic_eligible,
            filer_has_tin,
        )
        match = parameters(period).gov.states.il.tax.income.credits.eitc.match
        return state_eitc * match
