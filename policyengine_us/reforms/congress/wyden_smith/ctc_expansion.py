from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ctc_expansion() -> Reform:
    class refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "refundable CTC"
        unit = USD
        documentation = (
            "The portion of the Child Tax Credit that is refundable."
        )
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

        def formula(tax_unit, period, parameters):
            # This line corresponds to "the credit which would be allowed under this section [the CTC section]"
            # without regard to this subsection [the refundability section] and the limitation under
            # section 26(a) [the section that limits the amount of the non-refundable CTC to tax liability].
            # This is the full CTC. This is then limited to the maximum refundable amount per child as per the
            # TCJA provision.

            p_ctc = parameters(period).gov.irs.credits.ctc
            p_wyden_smith = parameters(period).gov.contrib.congress.wyden_smith

            maximum_amount = tax_unit("ctc_refundable_maximum", period)

            if p_ctc.refundable.fully_refundable:
                reduction = tax_unit("ctc_phase_out", period)
                return max_(0, maximum_amount - reduction)

            total_ctc = tax_unit("ctc", period)
            maximum_refundable_ctc = min_(maximum_amount, total_ctc)

            # The other part of the "lesser of" statement is: "the amount by which [the non-refundable CTC]
            # would increase if [tax liability] increased by tax_increase", where tax_increase is the greater of:
            # - the phase-in amount
            # - Social Security tax minus the EITC
            # First, we find tax_increase:

            current_year_earnings = tax_unit("tax_unit_earned_income", period)
            if p_wyden_smith.actc_lookback:
                prior_year_earnings = tax_unit(
                    "tax_unit_earned_income_last_year", period
                )
                earnings = max_(current_year_earnings, prior_year_earnings)
            else:
                earnings = current_year_earnings
            earnings_over_threshold = max_(
                0, earnings - p_ctc.refundable.phase_in.threshold
            )
            qualifying_children = tax_unit("ctc_qualifying_children", period)

            if p_wyden_smith.per_child_actc_phase_in:
                phase_in_rate = (
                    p_ctc.refundable.phase_in.rate * qualifying_children
                )
            else:
                phase_in_rate = p_ctc.refundable.phase_in.rate

            relevant_earnings = earnings_over_threshold * phase_in_rate

            # Compute "Social Security taxes" as defined in the US Code for the ACTC.
            # This includes OASDI and Medicare payroll taxes, as well as half
            # of self-employment taxes.
            SS_ADD_VARIABLES = [
                # Person:
                "employee_social_security_tax",
                "employee_medicare_tax",
                "unreported_payroll_tax",
                # Tax unit:
                "self_employment_tax_ald",
                "additional_medicare_tax",
            ]
            SS_SUBTRACT_VARIABLES = ["excess_payroll_tax_withheld"]
            social_security_tax = add(
                tax_unit, period, SS_ADD_VARIABLES
            ) - add(tax_unit, period, SS_SUBTRACT_VARIABLES)
            eitc = tax_unit("eitc", period)
            social_security_excess = max_(0, social_security_tax - eitc)
            qualifying_children = tax_unit("ctc_qualifying_children", period)
            tax_increase = where(
                qualifying_children
                < p_ctc.refundable.phase_in.min_children_for_ss_taxes_minus_eitc,
                relevant_earnings,
                max_(relevant_earnings, social_security_excess),
            )
            limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
            ctc_capped_by_tax = min_(total_ctc, limiting_tax)
            ctc_capped_by_increased_tax = min_(
                total_ctc, limiting_tax + tax_increase
            )
            amount_ctc_would_increase = (
                ctc_capped_by_increased_tax - ctc_capped_by_tax
            )

            return min_(maximum_refundable_ctc, amount_ctc_would_increase)

    class reform(Reform):
        def apply(self):
            self.update_variable(refundable_ctc)

    return reform


def create_ctc_expansion_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ctc_expansion()

    # Look ahead for the next five years

    p = parameters.gov.contrib.congress.wyden_smith

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if (
            p(current_period).actc_lookback
            or p(current_period).per_child_actc_phase_in
        ):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_expansion()
    else:
        return None


ctc_expansion = create_ctc_expansion_reform(None, None, bypass=True)
