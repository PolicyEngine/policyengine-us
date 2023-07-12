from policyengine_us.model_api import *


class id_grocery_credit_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "ID grocery credit refund"
    unit = USD
    definition_period = YEAR

    defined_for = "StateCode.ID"


    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.gc
        
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        person_over_65 = person("age", period) > p.65_older_eligibility
        return person * person_over_65 * p.amount
