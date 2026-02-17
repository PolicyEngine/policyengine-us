from policyengine_us.model_api import *


class mo_tanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF child care cost deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.child_care_deduction
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period.this_year)
        childcare_expenses = spm_unit("childcare_expenses", period)
        max_deduction_per_child = p.amount.calc(age) * dependent
        total_max_deduction = spm_unit.sum(max_deduction_per_child)
        return min_(childcare_expenses, total_max_deduction)
