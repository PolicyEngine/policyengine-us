from policyengine_us.model_api import *


class il_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) child care deduction "
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.143"  # (b)(2)
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.il.dhs.tanf.income.child_care_deduction
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        childcare_deduction_person = p.calc(age) * dependent
        total_childcare_deduction = spm_unit.sum(childcare_deduction_person)

        return min_(childcare_expenses, total_childcare_deduction)
