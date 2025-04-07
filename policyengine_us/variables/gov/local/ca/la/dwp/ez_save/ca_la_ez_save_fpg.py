from policyengine_us.model_api import *


class ca_la_ez_save_fpg(Variable):
    value_type = float
    entity = Household
    label = "Los Angeles County EZ save federal poverty guideline"
    unit = USD
    documentation = "The federal poverty guideline used to determine LA ez save eligibility."
    definition_period = MONTH
    defined_for = "in_la"

    def formula(household, period, parameters):
        p = parameters(period).gov.local.ca.la.dwp.ez_save.eligibility
        household_size = household("household_size", period.this_year)
        floored_household_size = max_(p.household_size_floor, household_size)
        state_group = household("state_group_str", period.this_year)
        year = period.start.year
        month = period.start.month
        if month >= 7:
            instant_str = f"{year}-07-01"
        else:
            instant_str = f"{year - 1}-07-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg

        p1 = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
        pn = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
        return p1 + pn * (floored_household_size - 1)
