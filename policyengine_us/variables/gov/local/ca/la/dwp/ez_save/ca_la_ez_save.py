from policyengine_us.model_api import *


class ca_la_ez_save(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Los Angeles County EZ Save program"
    defined_for = "ca_la_ez_save_eligible"

    def formula(household, period, parameters):
        electricity_expense = add(
            household, period, ["pre_subsidy_electricity_expense"]
        )
        p = parameters(period).gov.local.ca.la.dwp.ez_save
        uncapped_amount = p.amount
        return min_(electricity_expense, uncapped_amount)
