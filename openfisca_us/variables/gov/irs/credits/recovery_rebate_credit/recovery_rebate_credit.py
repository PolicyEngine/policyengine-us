from openfisca_us.model_api import *


class recovery_rebate_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recovery Rebate Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/6428"

    def formula(tax_unit, period, parameters):
        rrc = parameters(period).gov.irs.credits.recovery_rebate_credit
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        count_children = add(tax_unit, period, ["is_ctc_qualifying_child"]) # (a)(2) specifies CTC eligibility for children
        count_dependents = tax_unit("tax_unit_count_dependents", period)
        count_adults = where(tax_unit("tax_unit_is_joint", period), 2, 1)
        # First payment
        first_payment_max = (
            rrc.first.max.adult * count_adults
            + rrc.first.max.child * count_children
        )
        first_payment_reduction = rrc.first.phase_out.rate * max_(
            0,
            agi - rrc.first.phase_out.threshold[filing_status]
        )
        first_payment = max_(0, first_payment_max - first_payment_reduction)

        # Second payment
        second_payment_max = (
            rrc.second.max.adult * count_adults
            + rrc.second.max.child * count_children
        )
        second_payment_reduction = rrc.second.phase_out.rate * max_(
            0,
            agi - rrc.second.phase_out.threshold[filing_status]
        )
        second_payment = max_(0, second_payment_max - second_payment_reduction)

        # Third payment
        third_payment_max = (
            rrc.third.max.adult * count_adults
            + rrc.third.max.dependent * count_dependents
        )
        phase_out_length = rrc.third.phase_out.length[filing_status]
        third_payment_reduction = max_(
            0,
            agi - rrc.third.phase_out.threshold[filing_status]
        ) / phase_out_length * third_payment_max
        third_payment_reduction = where(
            phase_out_length == 0,
            0,
            third_payment_reduction,
        )
        third_payment = max_(0, third_payment_max - third_payment_reduction)
        return first_payment + second_payment + third_payment

