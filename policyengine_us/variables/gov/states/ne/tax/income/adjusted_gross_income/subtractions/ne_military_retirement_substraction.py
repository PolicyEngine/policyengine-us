from policyengine_us.model_api import *


class ne_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska military retirement subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.tax.income.agi.subtractions.military_retirement
        military_retirement_benefits = add(
            tax_unit, period, ["military_retirement_pay"]
        )
        return military_retirement_benefits * p.fraction
