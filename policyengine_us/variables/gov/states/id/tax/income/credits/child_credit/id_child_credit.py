from policyengine_us.model_api import *


class id_child_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho Child Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Get relevant parameter subtree.
        p = parameters(period).gov.states.id.tax.income.credits.child_credit
        # Count number of eligible children in the tax unit.
        age = person("age", period)
        eligible_child = age < p.age_eligibility
        eligible_children = tax_unit.sum(eligible_child)
        # Multiply by the amount per child.
        return eligible_children * p.amount
