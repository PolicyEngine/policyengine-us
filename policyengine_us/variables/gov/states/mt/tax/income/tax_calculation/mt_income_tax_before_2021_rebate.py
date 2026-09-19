from policyengine_us.model_api import *


class mt_income_tax_before_2021_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits and the 2021 rebate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    # The elected Montana income tax before refundable credits (Form 2 line 20),
    # excluding the 2021 income tax rebate. This is the liability the rebate is
    # capped against, and the base the rebate is subtracted from. Keeping it
    # rebate-free means the separate-vs-joint election does not depend on the
    # rebate (taxsim #1189).
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income
        indiv = add(tax_unit, period, ["mt_income_tax_before_refundable_credits_indiv"])
        joint = tax_unit("mt_income_tax_before_refundable_credits_joint", period)
        if p.married_filing_separately_on_same_return_allowed:
            return min_(indiv, joint)
        return joint
