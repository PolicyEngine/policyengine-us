from policyengine_us.model_api import *


class ctc_phase_in_relevant_earnings(Variable):
    value_type = float
    entity = TaxUnit
    label = "Relevant earnings for the CTC phase-in"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#d",
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        "https://www.law.cornell.edu/uscode/text/26/164#f",
    )

    def formula(tax_unit, period, parameters):

        ctc = parameters(period).gov.irs.credits.ctc

        # IRC 24(d)(1)(B)(i) defines earned income for the ACTC phase-in
        # as earned income "within the meaning of section 32", which per
        # IRC 32(c)(2)(A)(ii) is determined "with regard to the deduction
        # allowed to the taxpayer by section 164(f)" (half of SE tax).
        earnings = tax_unit("filer_adjusted_earnings", period)
        earnings_over_threshold = max_(
            0, earnings - ctc.refundable.phase_in.threshold
        )
        return earnings_over_threshold * ctc.refundable.phase_in.rate
