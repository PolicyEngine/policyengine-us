from policyengine_us.model_api import *


class ctc_phase_in(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC phase-in"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

    def formula(tax_unit, period, parameters):

        ctc = parameters(period).gov.irs.credits.ctc

        earnings = tax_unit("tax_unit_earned_income", period)
        earnings_over_threshold = max_(
            0, earnings - ctc.refundable.phase_in.threshold
        )
        relevant_earnings = (
            earnings_over_threshold * ctc.refundable.phase_in.rate
        )
        # The other part of the "lesser of" statement is: "the amount by which [the non-refundable CTC]
        # would increase if [tax liability] increased by tax_increase", where tax_increase is the greater of:
        # - the phase-in amount
        # - Social Security tax minus the EITC
        # First, we find tax_increase:

        social_security_tax = tax_unit("ctc_social_security_tax", period)
        eitc = tax_unit("eitc", period)
        social_security_excess = max_(0, social_security_tax - eitc)
        qualifying_children = tax_unit("ctc_qualifying_children", period)
        return where(
            qualifying_children
            < ctc.refundable.phase_in.min_children_for_ss_taxes_minus_eitc,
            relevant_earnings,
            max_(relevant_earnings, social_security_excess),
        )
