from policyengine_us.model_api import *


class ca_la_ez_save_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for the Los Angeles County EZ Save program"
    defined_for = "in_la"

    def formula(household, period, parameters):
        p = parameters(period).gov.local.ca.la.dwp.ez_save.eligibility
        income = add(household, period, ["ca_la_ez_save_countable_income"])
        household_size = household("household_size", period)
        floored_household_size = max_(p.household_size_floor, household_size)
        state_group = household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        fpg = p1 + pn * (floored_household_size - 1)
        income_limit = fpg * p.fpg_limit_increase
        return income <= income_limit
