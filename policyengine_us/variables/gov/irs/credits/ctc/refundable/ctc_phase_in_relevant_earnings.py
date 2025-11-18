from policyengine_us.model_api import *


class ctc_phase_in_relevant_earnings(Variable):
    value_type = float
    entity = TaxUnit
    label = "Relevant earnings for the CTC phase-in"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

    def formula(tax_unit, period, parameters):

        ctc = parameters(period).gov.irs.credits.ctc

        earnings = tax_unit("tax_unit_earned_income", period)
        earnings_over_threshold = max_(
            0, earnings - ctc.refundable.phase_in.threshold
        )
        return earnings_over_threshold * ctc.refundable.phase_in.rate
