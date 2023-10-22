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
        agi = tax_unit("adjusted_gross_income", period)
        income_threshold = p.income_threshold[filing_status]
        taxable_ss = add(tax_unit, period, ["taxable_social_security"])
        excess = tax_unit("ct_magi_excess_over_base", period)

        total_ss = add(tax_unit, period, ["social_security"])
        ss_fraction = total_ss * ss_rate
        max_inclusion = min_(ss_fraction, ss_rate * excess)
        adjusted_ss_benefit = max_(total_ss - max_inclusion, 0)
        return where(agi < income_threshold, total_ss, adjusted_ss_benefit)
