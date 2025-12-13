from policyengine_us.model_api import *


class mo_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF income eligibility (passes all three income tests)"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        gross = spm_unit("mo_tanf_gross_income_eligible", period)
        need = spm_unit("mo_tanf_standard_of_need_test", period)
        pct = spm_unit("mo_tanf_percentage_of_need_test", period)
        return gross & need & pct
