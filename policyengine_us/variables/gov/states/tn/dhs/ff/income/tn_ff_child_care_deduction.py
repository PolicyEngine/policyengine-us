from policyengine_us.model_api import *


class tn_ff_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First child care deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://publications.tnsosfiles.com/rules/1240/1240-01/1240-01-50.20081124.pdf#page=19"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ff.income.deductions
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        childcare_deduction_person = (
            p.child_care_deduction.calc(age) * dependent
        )
        total_childcare_deduction = spm_unit.sum(childcare_deduction_person)
        return min_(childcare_expenses, total_childcare_deduction)
