from policyengine_us.model_api import *


class refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "refundable CTC"
    unit = USD
    documentation = "The portion of the Child Tax Credit that is refundable."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#d",
        # No refundable CTC for filers electing a section 911 exclusion.
        "https://www.law.cornell.edu/uscode/text/26/24#d_3",
    )

    def formula(tax_unit, period, parameters):
        # This line corresponds to "the credit which would be allowed under this section [the CTC section]"
        # without regard to this subsection [the refundability section] and the limitation under
        # section 26(a) [the section that limits the amount of the non-refundable CTC to tax liability].
        # This is the full CTC. This is then limited to the maximum refundable amount per child as per the
        # TCJA provision.

        ctc = parameters(period).gov.irs.credits.ctc

        maximum_amount = tax_unit("ctc_refundable_maximum", period)

        total_ctc = tax_unit("ctc", period)

        if ctc.refundable.fully_refundable:
            reduction = tax_unit("ctc_phase_out", period)
            reduced_max_amount = max_(0, maximum_amount - reduction)
            return min_(reduced_max_amount, total_ctc)

        maximum_refundable_ctc = min_(maximum_amount, total_ctc)

        phase_in = tax_unit("ctc_phase_in", period)
        limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
        ctc_capped_by_tax = min_(total_ctc, limiting_tax)
        ctc_capped_by_increased_tax = min_(total_ctc, limiting_tax + phase_in)
        amount_ctc_would_increase = ctc_capped_by_increased_tax - ctc_capped_by_tax
        refundable_amount = min_(maximum_refundable_ctc, amount_ctc_would_increase)
        # Section 24(d)(3): the CTC is not refundable for a filer who elects to
        # exclude any amount from gross income under section 911 (Form 2555).
        barred = tax_unit("refundable_ctc_barred_by_section_911_exclusion", period)
        return where(barred, 0, refundable_amount)
