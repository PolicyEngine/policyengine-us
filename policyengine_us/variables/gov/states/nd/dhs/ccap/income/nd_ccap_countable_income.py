from policyengine_us.model_api import *


class nd_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP countable income"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.income
        gross_income = spm_unit("nd_ccap_gross_income", period)
        # The earned income of children under age 19 is excluded
        # (400-28-65-10-05; 400-28-65-15 #6; NDAC 75-02-01.3-08(12)).
        person = spm_unit.members
        is_minor = person("age", period.this_year) < p.child_earned_income_exclusion_age
        minor_earned_income = spm_unit.sum(
            is_minor
            * add(person, period, ["employment_income", "self_employment_income"])
        )
        child_support_deduction = spm_unit("nd_ccap_child_support_deduction", period)
        return max_(gross_income - minor_earned_income - child_support_deduction, 0)
