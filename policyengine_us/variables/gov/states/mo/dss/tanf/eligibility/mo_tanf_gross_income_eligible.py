from policyengine_us.model_api import *


class mo_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF gross income eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-05-185/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        standard_of_need = spm_unit("mo_tanf_standard_of_need", period)
        limit = standard_of_need * p.income_limit.rate
        return gross_income < limit
