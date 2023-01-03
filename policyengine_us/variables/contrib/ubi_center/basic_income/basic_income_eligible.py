from policyengine_us.model_api import *


class basic_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Basic income eligible"
    unit = USD
    documentation = (
        "Eligible for basic income payments based on adjusted gross income."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.ubi_center.basic_income.agi_limit
        if not p.in_effect:
            return True
        agi_limit = p.amount[tax_unit("filing_status", period)]
        return tax_unit("adjusted_gross_income", period) <= agi_limit
