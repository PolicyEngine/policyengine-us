from policyengine_us.model_api import *


class rrc_caa(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recovery Rebate Credit (CAA)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/6428A"

    def formula(tax_unit, period, parameters):
        rrc = parameters(period).gov.irs.credits.recovery_rebate_credit
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        # (a)(2) specifies CTC eligibility for children
        count_children = tax_unit("ctc_qualifying_children", period)
        count_adults = where(tax_unit("tax_unit_is_joint", period), 2, 1)
        max_payment = (
            rrc.caa.max.adult * count_adults
            + rrc.caa.max.child * count_children
        )
        payment_reduction = rrc.caa.phase_out.rate * max_(
            0, agi - rrc.caa.phase_out.threshold[filing_status]
        )
        return max_(0, max_payment - payment_reduction)
