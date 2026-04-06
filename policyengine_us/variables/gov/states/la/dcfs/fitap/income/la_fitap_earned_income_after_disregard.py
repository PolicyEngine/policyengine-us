from policyengine_us.model_api import *


class la_fitap_earned_income_after_disregard(Variable):
    value_type = float
    entity = Person
    label = "Louisiana FITAP earned income after disregard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/louisiana/La-Admin-Code-tit-67-SS-III-1229"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.dcfs.fitap.income.deductions
        gross_earned = person("tanf_gross_earned_income", period)

        # Per LAC 67:III.1229.C:
        # 1. Apply $120 standard deduction
        # 2. Apply $900 time-limited deduction (6-month limit not modeled yet)
        after_standard = max_(gross_earned - p.standard, 0)
        return max_(after_standard - p.time_limited, 0)
