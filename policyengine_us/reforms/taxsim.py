from policyengine_core.reforms import Reform
from policyengine_us.model_api import *
import numpy as np
from policyengine_us.variables.gov.states.pa.tax.income.forgiveness.pa_tax_forgiveness_rate import (
    pa_tax_forgiveness_rate as baseline_pa_tax_forgiveness_rate,
)
from policyengine_us.variables.gov.irs.credits.ctc.refundable.ctc_refundable_maximum import (
    ctc_refundable_maximum as baseline_ctc_refundable_maximum,
)
from policyengine_us.variables.gov.irs.credits.ctc.phase_out.arpa.ctc_arpa_uncapped_phase_out import (
    ctc_arpa_uncapped_phase_out as baseline_ctc_arpa_uncapped_phase_out,
)
from policyengine_us.variables.gov.irs.credits.ctc.phase_out.ctc_phase_out import (
    ctc_phase_out as baseline_ctc_phase_out,
)


class pa_tax_forgiveness_rate(baseline_pa_tax_forgiveness_rate):
    """
    TAXSIM erroneously phases in tax forgiveness smoothly.
    """

    def formula(tax_unit, period, parameters):
        eligibility_income = tax_unit("pa_eligibility_income", period)
        person = tax_unit.members
        is_child_dependent = person("is_child_of_tax_head", period) & person(
            "is_tax_unit_dependent", period
        )
        child_dependents = tax_unit.sum(is_child_dependent)
        # filing status affects the base, where it doubles for married claimants
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint_separate = (filing_status == filing_statuses.JOINT) | (
            filing_status == filing_statuses.SEPARATE
        )
        base_multiplier = where(joint_separate, 2, 1)
        p = parameters(period).gov.states.pa.tax.income.forgiveness
        base = p.base * base_multiplier
        rate_per_dependent = p.dependent_rate
        eligibility_income_increment = base + (
            rate_per_dependent * child_dependents
        )
        excess = eligibility_income - eligibility_income_increment
        forgiveness_increment = p.rate_increment
        increments = excess / forgiveness_increment
        percent = p.tax_back
        return min_(max_(1 - percent * increments, 0), 1)


class ctc_refundable_maximum(baseline_ctc_refundable_maximum):
    """
    TAXSIM erroneously makes the adult CTC refundable as well.
    """

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Use either normal or ARPA CTC maximums.
        child_amount = max_(
            person("ctc_child_individual_maximum", period),
            person("ctc_child_individual_maximum_arpa", period),
        )
        adult_amount = person("ctc_adult_individual_maximum", period)
        ctc = parameters(period).gov.irs.credits.ctc
        if ctc.refundable.fully_refundable:
            # Fully refundable CTC does not affect the adult CTC.
            return tax_unit.sum(child_amount + adult_amount)
        return tax_unit.sum(min_(child_amount, ctc.refundable.individual_max))


class ctc_arpa_uncapped_phase_out(baseline_ctc_arpa_uncapped_phase_out):
    """
    TAXSIM erroneously phases out the CTC smoothly rather than in increments.
    """

    def formula(tax_unit, period, parameters):
        # Logic sequence follows the form, which is clearer than the IRC.
        p = parameters(period).gov.irs.credits.ctc.phase_out.arpa
        # defined_for didn't work.
        if not p.in_effect:
            return 0
        # The ARPA CTC has two phase-outs: the original, and a new phase-out
        # applying before and only to the increase in the maximum CTC under ARPA.
        # Calculate the income used to assess the new phase-out.
        threshold = tax_unit("ctc_arpa_phase_out_threshold", period)
        agi = tax_unit("adjusted_gross_income", period)
        excess = max_(0, agi - threshold)
        return excess * p.amount / p.increment


class ctc_phase_out(baseline_ctc_phase_out):
    """
    TAXSIM erroneously phases out the CTC smoothly rather than in increments.
    """

    def formula(tax_unit, period, parameters):
        # TCJA's phase-out changes are purely parametric so don't require
        # structural reform.

        # The ARPA CTC has two phase-outs: the original, and a new phase-out
        # applying before and only to the increase in the maximum CTC under ARPA.

        # Start with the normal phase-out.
        income = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.irs.credits.ctc.phase_out
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        excess = max_(0, income - phase_out_threshold)
        return excess * p.amount / p.increment


class taxsim(Reform):
    def apply(self):
        self.update_variable(pa_tax_forgiveness_rate)
        self.update_variable(ctc_refundable_maximum)
        self.update_variable(ctc_arpa_uncapped_phase_out)
        self.update_variable(ctc_phase_out)
