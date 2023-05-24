from policyengine_us.model_api import *


class id_child_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho Child Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Get relevant parameter subtree.
        p = parameters(period).gov.states.id.tax.income.credits.child_credit
        # Determine eligibility for each person in the tax unit.
        person = tax_unit.members
        meets_age_limit = person("age", period) < p.eligible_age
        eligible = meets_age_limit & person("is_child_of_tax_head", period)
        # Count number of eligible children in the tax unit.
        count_eligible = tax_unit.sum(eligible)
        # Multiply by the amount per child.
        return count_eligible * p.amount
