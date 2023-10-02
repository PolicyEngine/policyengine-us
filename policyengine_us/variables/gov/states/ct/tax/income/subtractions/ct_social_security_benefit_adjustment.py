from policyengine_us.model_api import *


class ct_social_security_benefit_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit subtraction"
    definition_period = YEAR
    defined_for = "ct_social_security_benefit_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        income_base_amount = p.threshold.lower
        ss_agi_frac = p.rate.lower
        filing_status = tax_unit("filing_status", period)
        base_amount = income_base_amount[filing_status]
        ss_rate = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.social_security.rate
        # is_eligible = tax_unit(
        #     "ct_social_security_benefit_adjustment_eligible", period
        # )
        ss_benefit = add(tax_unit, period, ["social_security"])
        agi = add(tax_unit, period, ["adjusted_gross_income"])

        includable_ss = ss_benefit * ss_rate
        excess = agi + ss_agi_frac * ss_benefit - base_amount
        max_inclusion = min_(includable_ss, ss_rate * excess)
        adjusted_ss_benefit = max_(max_inclusion - includable_ss, 0)
        # return where(is_eligible, 0, adjusted_ss_benefit)
        return adjusted_ss_benefit
