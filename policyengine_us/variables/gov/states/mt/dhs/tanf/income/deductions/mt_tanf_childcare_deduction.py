from policyengine_us.model_api import *


class mt_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) child care deduction "
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/tanf602-1jan012018.pdf"
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.dhs.tanf.income.deductions.child_care
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        child = person("is_child", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        childcare_deduction_person = p.amount.value * (child & dependent)
        total_childcare_deduction = spm_unit.sum(childcare_deduction_person)

        return min_(childcare_expenses, total_childcare_deduction)
