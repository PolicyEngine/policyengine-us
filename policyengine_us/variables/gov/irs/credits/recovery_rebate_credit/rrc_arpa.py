from policyengine_us.model_api import *


class rrc_arpa(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recovery Rebate Credit (ARPA)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/6428B"

    def formula(tax_unit, period, parameters):
        rrc = parameters(period).gov.irs.credits.recovery_rebate_credit
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        count_dependents = tax_unit("tax_unit_count_dependents", period)
        count_adults = where(tax_unit("tax_unit_is_joint", period), 2, 1)
        max_payment = (
            rrc.arpa.max.adult * count_adults
            + rrc.arpa.max.dependent * count_dependents
        )
        phase_out_length = rrc.arpa.phase_out.length[filing_status]
        excess = max_(0, agi - rrc.arpa.phase_out.threshold[filing_status])
        payment_reduction_percent = excess / phase_out_length
        payment_reduction = max_payment * payment_reduction_percent
        return max_(0, max_payment - payment_reduction)
