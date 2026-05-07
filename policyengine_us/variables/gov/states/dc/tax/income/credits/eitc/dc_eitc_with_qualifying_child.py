from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.credits.eitc_helpers import (
    calculate_eitc_like_amount,
)


class dc_eitc_with_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC with qualifying children"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        qualifying_child = person("is_qualifying_child_dependent", period) & has_tin
        child_count = tax_unit.sum(qualifying_child)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        federal_like_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count,
            child_count > 0,
            filer_has_tin,
        )
        p = parameters(period).gov.states.dc.tax.income.credits
        return federal_like_eitc * p.eitc.with_children.match
