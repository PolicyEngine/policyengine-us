from policyengine_us.model_api import *


class id_grocery_credit_enhancement_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the enhancement of the Idaho grocery credit"
    definition_period = YEAR
    defined_for = "id_grocery_credit_enhancement_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.gc

        #  use id_grocery_credit_enhancement_eligible in defined for and get number of dependents * the amount ($100) as a parameter
        dependents = tax_unit("tax_unit_dependents", period)
        base_credit = p.amount  # 100

        return dependents * base_credit
