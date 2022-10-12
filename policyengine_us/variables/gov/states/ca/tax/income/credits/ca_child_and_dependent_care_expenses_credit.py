from policyengine_us.model_api import *


class ca_child_and_dependent_care_expenses_credit(Variable):
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
        ).gov.states.ca.tax.income.credits.child_and_dependent_care_expenses
        agi = tax_unit("adjusted_gross_income", period)
        federal_cdcc = tax_unit("cdcc", period)
        multiplier_1 = p.multiplier_1.calc(agi)
        multiplier_2 = p.multiplier_2.calc(agi)
        return federal_cdcc * multiplier_1 * multiplier_2
