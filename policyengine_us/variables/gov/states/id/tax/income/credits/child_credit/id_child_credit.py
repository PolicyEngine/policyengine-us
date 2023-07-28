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
        # check if child is eligible
        eligible_age = p.age_eligibility
        person = tax_unit.members
        print(person("age", period))
        # Count number of eligible children in the tax unit.
        count_eligible = sum(
            [
                age <= eligible_age
                for age in person("age", period)
            ])
        #count_eligible = tax_unit("ctc_qualifying_children", period)
        # Multiply by the amount per child.
        return count_eligible * p.amount
