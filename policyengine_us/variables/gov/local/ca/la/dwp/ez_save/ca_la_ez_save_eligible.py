from policyengine_us.model_api import *


class ca_la_ez_save_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Eligible for the Los Angeles County EZ Save program"
    defined_for = "in_la"

    def formula(household, period, parameters):
        income = household("ca_la_ez_save_countable_income", period)
        fpg = household("ca_la_ez_save_fpg", period)
        p = parameters(period).gov.local.ca.la.dwp.ez_save.eligibility
        income_limit = fpg * p.fpg_limit_increase
        return income <= income_limit
