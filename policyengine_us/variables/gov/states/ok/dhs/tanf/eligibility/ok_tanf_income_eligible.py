from policyengine_us.model_api import *


class ok_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oklahoma TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-27"
    )
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.tanf.income

        # Per OAC 340:10-3-27: Gross income limit = 185% of State Standard of Need
        unit_size = spm_unit("spm_unit_size", period)
        need_standard = p.need_standard.calc(unit_size)
        gross_income_limit = need_standard * p.gross_income_limit_rate

        # Gross income test uses gross income (before disregards)
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        return gross_income <= gross_income_limit
