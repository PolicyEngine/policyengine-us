from policyengine_us.model_api import *


class dc_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) child care deduction "
    unit = USD
    definition_period = MONTH
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"  # (A)(2)
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.income.deductions.child_care
        person = spm_unit.members
        child = person("is_child", period)
        dependent = person("is_tax_unit_dependent", period)
        eligible_child = child & dependent
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        childcare_deduction_person = p.amount.calc(age) * eligible_child
        total_childcare_deduction = spm_unit.sum(childcare_deduction_person)

        return min_(childcare_expenses, total_childcare_deduction)
