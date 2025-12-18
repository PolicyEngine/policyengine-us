from policyengine_us.model_api import *


class mo_tanf_standard_of_need_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF Standard of Need test eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        standard_of_need = spm_unit("mo_tanf_standard_of_need", period)
        income = spm_unit("mo_tanf_income_for_need_test", period)
        return income < standard_of_need
