from policyengine_us.model_api import *


class ca_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Child and Dependent Care Expenses Credit"
    unit = USD
    documentation = (
        "https://www.ftb.ca.gov/forms/2020/2020-3506-instructions.html"
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.tax.income.credits.child_dependent_care
        agi = tax_unit("adjusted_gross_income", period)
        federal_cdcc = add(tax_unit, period, p.input)
        rate = p.rate.calc(agi)
        return federal_cdcc * rate
