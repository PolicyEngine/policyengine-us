from policyengine_us.model_api import *


class id_grocery_credit_enhancement(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Idaho grocery credit enhancement"
    definition_period = YEAR
    defined_for = "id_grocery_credit_enhancement_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.gc

        # use id_grocery_credit_enhancement_eligible in defined for and get number of dependents * the amount of credit as a parameter

        dependents = tax_unit("tax_unit_dependents", period)

        return dependents * p.amount
