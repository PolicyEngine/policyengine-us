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
        income = spm_unit("mo_tanf_countable_income", period)
        limit = spm_unit("mo_tanf_maximum_benefit", period)
        return income < limit
