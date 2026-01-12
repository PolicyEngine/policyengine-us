from policyengine_us.model_api import *


class mo_tanf_percentage_of_need_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF Percentage of Need test eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-15/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf
        standard_of_need = spm_unit("mo_tanf_standard_of_need", period)
        income = spm_unit("mo_tanf_countable_income", period)
        limit = standard_of_need * p.maximum_benefit.percentage
        return income < limit
