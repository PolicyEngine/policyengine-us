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
        ss_rate = p.rate
        agi = add(tax_unit, period, ["adjusted_gross_income"])
        income_threshold = p.income_threshold[filing_status]
        ss_benefit = add(tax_unit, period, ["taxable_social_security"])
        excess = tax_unit("ct_magi_excess_over_base", period)

        includable_ss = ss_benefit * ss_rate
        max_inclusion = min_(includable_ss, ss_rate * excess)
        adjusted_ss_benefit = max_(ss_benefit - max_inclusion, 0)
        return where(agi < income_threshold, ss_benefit, adjusted_ss_benefit)
