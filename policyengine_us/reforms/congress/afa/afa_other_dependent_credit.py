from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_afa_other_dependent_credit() -> Reform:
    class other_dependent_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Other Dependent Credit which is independent of the CTC"
        unit = USD
        documentation = (
            "The standalone dependent credit in respect of this person."
        )
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(tax_unit, period, parameters):
            maximum_amount = add(
                tax_unit, period, ["other_dependent_credit_maximum"]
            )
            reduction = tax_unit("other_dependent_credit_phase_out", period)
            return max_(0, maximum_amount - reduction)

    class other_dependent_credit_maximum(Variable):
        value_type = float
        entity = Person
        label = "Other Dependent Credit Maximum"
        unit = USD
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.afa.other_dependent_credit
            is_dependent = person("is_tax_unit_dependent", period)
            is_child = person("ctc_child_individual_maximum", period) > 0
            is_adult_dependent = ~is_child & is_dependent
            return is_adult_dependent * p.amount

    class other_dependent_credit_phase_out(Variable):
        value_type = float
        entity = TaxUnit
        label = "Other Dependent Credit Phase-Out"
        unit = USD
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(tax_unit, period, parameters):
            # TCJA's phase-out changes are purely parametric so don't require
            # structural reform.

            # The ARPA CTC has two phase-outs: the original, and a new phase-out
            # applying before and only to the increase in the maximum CTC under ARPA.

            # Start with the normal phase-out.
            income = tax_unit("adjusted_gross_income", period)
            p = parameters(period).gov.contrib.congress.afa.ctc.phase_out
            filing_status = tax_unit("filing_status", period)
            phase_out_threshold = p.threshold.higher[filing_status]
            excess = max_(0, income - phase_out_threshold)
            increments = np.ceil(excess / p.increment)
            return increments * p.amount

    class ctc_lower_phase_out(Variable):
        value_type = float
        entity = TaxUnit
        label = "CTC reduction from income"
        unit = USD
        documentation = "Reduction of the total CTC due to income."
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(tax_unit, period, parameters):
            # TCJA's phase-out changes are purely parametric so don't require
            # structural reform.

            # The ARPA CTC has two phase-outs: the original, and a new phase-out
            # applying before and only to the increase in the maximum CTC under ARPA.

            # Start with the normal phase-out.
            income = tax_unit("adjusted_gross_income", period)
            p = parameters(period).gov.contrib.congress.afa.ctc.phase_out
            filing_status = tax_unit("filing_status", period)
            lower_threshold = p.threshold.lower[filing_status]
            excess = max_(0, income - lower_threshold)
            increments = np.ceil(excess / p.increment)
            return increments * p.amount

    class ctc_higher_phase_out(Variable):
        value_type = float
        entity = TaxUnit
        label = "CTC reduction from income"
        unit = USD
        documentation = "Reduction of the total CTC due to income."
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(tax_unit, period, parameters):
            # TCJA's phase-out changes are purely parametric so don't require
            # structural reform.

            # The ARPA CTC has two phase-outs: the original, and a new phase-out
            # applying before and only to the increase in the maximum CTC under ARPA.

            # Start with the normal phase-out.
            income = tax_unit("adjusted_gross_income", period)
            p = parameters(period).gov.contrib.congress.afa.ctc.phase_out
            filing_status = tax_unit("filing_status", period)
            lower_threshold = p.threshold.higher[filing_status]
            excess = max_(0, income - lower_threshold)
            increments = np.ceil(excess / p.increment)
            return increments * p.amount

    class refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "refundable CTC"
        unit = USD
        documentation = (
            "The portion of the Child Tax Credit that is refundable."
        )
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

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
                reduction = tax_unit("ctc_lower_phase_out", period)
                p = parameters(period).gov.contrib.congress.afa.ctc.phase_out
                qualifying_children = tax_unit(
                    "ctc_qualifying_children", period
                )
                lower_floor = p.lower_floor * qualifying_children
                capped_credit = min_(lower_floor, maximum_amount)
                reduced_max_amount_lower = max_(
                    capped_credit, maximum_amount - reduction
                )
                higher_reduction = tax_unit("ctc_higher_phase_out", period)
                reduced_max_amount = max_(
                    0, reduced_max_amount_lower - higher_reduction
                )
                return min_(reduced_max_amount, total_ctc)

            maximum_refundable_ctc = min_(maximum_amount, total_ctc)

            phase_in = tax_unit("ctc_phase_in", period)
            limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
            ctc_capped_by_tax = min_(total_ctc, limiting_tax)
            ctc_capped_by_increased_tax = min_(
                total_ctc, limiting_tax + phase_in
            )
            amount_ctc_would_increase = (
                ctc_capped_by_increased_tax - ctc_capped_by_tax
            )
            return min_(maximum_refundable_ctc, amount_ctc_would_increase)

    class ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Child Tax Credit"
        unit = USD
        documentation = "Total value of the non-refundable and refundable portions of the Child Tax Credit."
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(tax_unit, period, parameters):
            maximum_amount = add(
                tax_unit, period, ["ctc_child_individual_maximum_arpa"]
            )
            reduction = tax_unit("ctc_lower_phase_out", period)
            p = parameters(period).gov.contrib.congress.afa.ctc.phase_out
            qualifying_children = tax_unit("ctc_qualifying_children", period)
            lower_floor = p.lower_floor * qualifying_children
            reduced_max_amount_lower = max_(
                lower_floor, maximum_amount - reduction
            )
            higher_reduction = tax_unit("ctc_higher_phase_out", period)
            return max_(0, reduced_max_amount_lower - higher_reduction)

    class ctc_child_individual_maximum_arpa(Variable):
        value_type = float
        entity = Person
        label = "CTC maximum amount (child under ARPA)"
        unit = USD
        documentation = "The CTC entitlement in respect of this person as a child, under the American Rescue Plan Act."
        definition_period = YEAR
        reference = "https://www.bennet.senate.gov/wp-content/uploads/2025/04/American-Family-Act-2025.pdf"

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.congress.afa.ctc.amount
            base_amount = p.base
            age = person("age", period)
            multiplier = p.multiplier.calc(age)
            pre_baby_bonus_amount = base_amount * multiplier
            is_baby = age < 1
            monthly_base_amount = base_amount / MONTHS_IN_YEAR
            baby_bonus = (
                monthly_base_amount * p.baby_bonus
                - monthly_base_amount * multiplier
            )
            baby_bonus_amount = baby_bonus * is_baby
            return pre_baby_bonus_amount + baby_bonus_amount

    def modify_parameters(parameters):
        parameters.gov.irs.credits.non_refundable.update(
            start=instant("2025-01-01"),
            stop=instant("2039-12-31"),
            value=[
                "cdcc",
                "elderly_disabled_credit",
                "non_refundable_american_opportunity_credit",
                "lifetime_learning_credit",
                "savers_credit",
                "residential_clean_energy_credit",
                "energy_efficient_home_improvement_credit",
                "new_clean_vehicle_credit",
                "used_clean_vehicle_credit",
                "other_dependent_credit",
            ],
        )
        parameters.gov.irs.credits.ctc.refundable.fully_refundable.update(
            start=instant("2025-01-01"),
            stop=instant("2039-12-31"),
            value=True,
        )
        parameters.gov.irs.credits.ctc.amount.base[1].threshold.update(
            start=instant("2025-01-01"),
            stop=instant("2039-12-31"),
            value=18,
        )
        parameters.gov.irs.credits.ctc.amount.adult_dependent.update(
            start=instant("2025-01-01"),
            stop=instant("2039-12-31"),
            value=0,
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(other_dependent_credit_maximum)
            self.update_variable(other_dependent_credit_phase_out)
            self.update_variable(other_dependent_credit)
            self.update_variable(ctc_lower_phase_out)
            self.update_variable(ctc_higher_phase_out)
            self.update_variable(ctc)
            self.update_variable(refundable_ctc)
            self.update_variable(ctc_child_individual_maximum_arpa)
            self.modify_parameters(modify_parameters)

    return reform


def create_afa_other_dependent_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_afa_other_dependent_credit()

    p = parameters.gov.contrib.congress.afa
    reform_active = False
    current_period = period_(period)

    for i in range(10):
        if p.in_effect(current_period):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_afa_other_dependent_credit()
    else:
        return None


afa_other_dependent_credit = create_afa_other_dependent_credit_reform(
    None, None, bypass=True
)
