from policyengine_us.model_api import *


class la_ez_save_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County EZ Save program"
    defined_for = "in_la"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.la.dwp.ez_save.eligibility
        income = spm_unit("la_ez_save_countable_income", period)
        household_size = spm_unit("spm_unit_size", period)
        increased_household_size = max_(p.min_unit_size, household_size)
        state_group = spm_unit.household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group] 
        fpg = p1 + pn * (increased_household_size - 1)
        increased_fpg = fpg * p.fpg_limit_increase
        return income <= increased_fpg
