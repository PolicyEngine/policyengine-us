from openfisca_us.model_api import *

# Disable divide-by-zero warning for this file
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)


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
        payment_reduction = (
            max_(0, agi - rrc.arpa.phase_out.threshold[filing_status])
            / phase_out_length
            * max_payment
        )
        payment_reduction = where(
            phase_out_length == 0,
            0,
            payment_reduction,
        )
        return max_(0, max_payment - payment_reduction)
