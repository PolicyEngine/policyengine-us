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
        fpg = spm_unit("spm_unit_fpg", period.this_year)
        gross_income_limit = fpg * p.gross_income_limit_rate / MONTHS_IN_YEAR

        # Use federal baseline for gross income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        gross_income = gross_earned + gross_unearned

        # Must pass gross income test (130% FPL)
        passes_gross_test = gross_income <= gross_income_limit

        # Must also have countable income <= payment standard
        countable_income = spm_unit("nv_tanf_countable_income", period)
        payment_standard = spm_unit("nv_tanf_payment_standard", period)
        passes_net_test = countable_income <= payment_standard

        return passes_gross_test & passes_net_test
