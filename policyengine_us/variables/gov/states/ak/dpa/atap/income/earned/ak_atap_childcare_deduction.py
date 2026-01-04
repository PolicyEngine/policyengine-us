from policyengine_us.model_api import *


class ak_atap_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP childcare deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.485"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Per 7 AAC 45.485: Child care expenses excluded up to:
        # - $200/month per child under age 2
        # - $175/month per child age 2 and older
        p = parameters(period).gov.states.ak.dpa.atap.income.deductions
        person = spm_unit.members
        age = person("age", period.this_year)
        is_child = person("is_child", period.this_year)
        # Only count children, not adults
        max_per_child = p.child_care_disregard.calc(age) * is_child
        total_max_disregard = spm_unit.sum(max_per_child)
        childcare_expenses = spm_unit("childcare_expenses", period)
        return min_(childcare_expenses, total_max_disregard)
