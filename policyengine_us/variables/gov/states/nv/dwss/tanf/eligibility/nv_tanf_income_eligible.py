from policyengine_us.model_api import *


class nv_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nevada TANF income eligible"
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-2/"
    defined_for = StateCode.NV

    def formula(spm_unit, period, parameters):
        # Nevada uses 130% FPL as gross income test
        p = parameters(period).gov.states.nv.dwss.tanf.income
        fpg = spm_unit("spm_unit_fpg", period)
        gross_income_limit = fpg * p.gross_income_limit_rate

        # Use federal baseline for gross income
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        # Must pass gross income test (130% FPL)
        passes_gross_test = gross_income <= gross_income_limit

        # Must also have countable income <= 100% Need Standard
        # Per C-140.1: Need Standard is used for eligibility determination
        countable_income = spm_unit("nv_tanf_countable_income", period)
        need_standard = spm_unit("nv_tanf_need_standard", period)
        passes_net_test = countable_income <= need_standard

        return passes_gross_test & passes_net_test
