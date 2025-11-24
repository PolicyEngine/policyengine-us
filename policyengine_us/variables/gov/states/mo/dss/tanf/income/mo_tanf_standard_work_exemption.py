from policyengine_us.model_api import *


class mo_tanf_standard_work_exemption(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF standard work exemption from earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.earned_income_disregard
        gross_earned_income = spm_unit("mo_tanf_gross_earned_income", period)

        # Standard work exemption is the lesser of earned income or the exemption amount
        return min_(gross_earned_income, p.standard_work_exemption)
