from policyengine_us.model_api import *


class tn_ff_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee Families First income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20"
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        p = parameters(period).gov.states.tn.dhs.ff
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.payment.max_family_size)

        cns = p.payment.consolidated_need_standard[capped_size]
        gis = cns * p.income.rate
        gross_income_test = gross_income <= gis

        countable_income = spm_unit("tn_ff_countable_income", period)
        net_income_test = countable_income < cns

        return gross_income_test & net_income_test
