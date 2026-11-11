from policyengine_us.model_api import *


class co_ccap_child_charges(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program charges for the child's care"
    documentation = "The child's child care and after-school charges, floored at zero."
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        charges = add(
            person,
            period,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        return max_(charges, 0)
