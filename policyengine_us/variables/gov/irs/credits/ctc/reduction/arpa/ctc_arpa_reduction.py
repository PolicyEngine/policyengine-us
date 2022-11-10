from policyengine_us.model_api import *


class ctc_arpa_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Additional CTC ARPA reduction"
    unit = USD
    documentation = "Additional ARPA reduction of the total CTC due to income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).gov.irs.credits.ctc
        # defined_for didn't work.
        if not ctc.phase_out.arpa.in_effect:
            return 0
        # The ARPA CTC has two phase-outs: the original, and a new phase-out
        # applying before and only to the increase in the maximum CTC under ARPA.
        # Calculate the income used to assess the new phase-out.
        filing_status = tax_unit("filing_status", period)
        arpa_threshold = ctc.phase_out.arpa.threshold[filing_status]
        income = tax_unit("adjusted_gross_income", period)
        income_over_arpa_threshold = max_(0, income - arpa_threshold)
        arpa_phase_out_max_reduction = (
            ctc.phase_out.arpa.rate * income_over_arpa_threshold
        )

        # Calculate the increase - do this by finding the original CTC if
        # ARPA had not applied - this year's variables, last year's parameters.
        ctc_maximum = tax_unit("ctc_maximum", period)
        ctc_maximum_without_arpa = tax_unit("ctc_maximum_without_arpa", period)
        arpa_increase = ctc_maximum - ctc_maximum_without_arpa

        arpa_phase_out_range = (
            tax_unit("ctc_phase_out_threshold", period) - arpa_threshold
        )

        # Apply the phase-out
        arpa_reduction_max = min_(
            arpa_increase, ctc.phase_out.arpa.rate * arpa_phase_out_range
        )

        return min_(arpa_phase_out_max_reduction, arpa_reduction_max)
