from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit adjustment"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.social_security
        filing_status = tax_unit("filing_status", period)
        is_eligible = tax_unit("ct_social_security_benefit_adjustment_eligible", period)
        ss_benefit = add(tax_unit, period, ["social_security"])
        agi = add(tax_unit, period, ["adjusted_gross_income"])
        base_amount = p.base_amount[filing_status]
        ss_benefit_frac = parameters(period).gov.states.ct.tax.income.subtractions.social_security.ss_fraction
        ss_agi_frac = parameters(period).gov.states.ct.tax.income.subtractions.social_security.excess_fraction
        includable_ss = ss_benefit * ss_benefit_frac
        excess = agi + ss_agi_frac * ss_benefit - base_amount
        max_inclusion = min_(includable_ss, ss_benefit_frac * excess)
        adjusted_ss_benefit = max_(max_inclusion - includable_ss, 0)
        return where(is_eligible, 0, adjusted_ss_benefit)