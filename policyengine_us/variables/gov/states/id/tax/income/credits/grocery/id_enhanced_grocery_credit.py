from policyengine_us.model_api import *


class id_enhanced_grocery_credit(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Idaho grocery credit enhancement"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.grocery.amount

        # get number of dependents * the amount of credit as a parameter

        dependents = tax_unit("tax_unit_dependents", period)

        return dependents * p.base
