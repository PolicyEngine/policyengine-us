from policyengine_us.model_api import *


class mo_tanf_income_for_standard_of_need_test(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF income for Standard of Need test"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.earned_income_disregard
        gross_earned_income = add(
            spm_unit, period, ["mo_tanf_gross_earned_income"]
        )
        unearned_income = spm_unit("mo_tanf_unearned_income", period)

        # For Standard of Need test: $90 exemption, child care, and student exemption
        # (student exemption not implemented in simplified version)
        standard_work_exemption = min_(
            gross_earned_income, p.standard_work_exemption
        )
        child_care_deduction = spm_unit("mo_tanf_child_care_deduction", period)

        total_income = gross_earned_income + unearned_income
        deductions = standard_work_exemption + child_care_deduction

        return max_(total_income - deductions, 0)
