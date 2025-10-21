from policyengine_us.model_api import *


class fl_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TANF income eligible"
    definition_period = YEAR
    reference = "Florida Statute § 414.095"
    documentation = "Meets income test: gross income less than 185% FPL and net countable income at or below payment standard"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf

        # Gross income test (185% FPL)
        gross_earned = spm_unit("fl_tanf_gross_earned_income", period)
        gross_unearned = spm_unit("fl_tanf_gross_unearned_income", period)
        total_gross = gross_earned + gross_unearned

        family_size = spm_unit.nb_persons()

        # Annual gross income limit (185% FPL)
        annual_limit = p.income_limits.gross_income_limit.calc(family_size)

        gross_income_eligible = total_gross < annual_limit

        # Net countable income test (must be at or below payment standard)
        countable_income = spm_unit("fl_tanf_countable_income", period)
        payment_standard = spm_unit("fl_tanf_payment_standard", period)

        net_income_eligible = countable_income <= payment_standard

        return gross_income_eligible & net_income_eligible
