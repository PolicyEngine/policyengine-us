from policyengine_us.model_api import *


class ny_allowable_college_tuition_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York allowable college tuition expenses for the credit and deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606"  # (t)(2)(A)
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.college_tuition
        person = tax_unit.members
        capped = min_(person("qualified_tuition_expenses", period), p.cap)
        return tax_unit.sum(capped)
