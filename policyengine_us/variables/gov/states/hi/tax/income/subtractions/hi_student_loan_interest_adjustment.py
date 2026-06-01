from policyengine_us.model_api import *


class hi_student_loan_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = "https://files.hawaii.gov/tax/forms/current/n11ins.pdf#page=35"

    def formula(tax_unit, period, parameters):
        # HRS § 235-2.4 / N-11 Instructions p.35 — gate on whether Hawaii's
        # static-conformity student loan interest deduction is in effect.
        p_sli = parameters(
            period
        ).gov.states.hi.tax.income.subtractions.student_loan_interest
        if not p_sli.in_effect:
            return 0
        person = tax_unit.members
        eligible = person("student_loan_interest_ald_eligible", period)
        interest_paid = tax_unit.sum(person("student_loan_interest", period) * eligible)
        capped_interest = min_(interest_paid, p_sli.cap)

        hi_magi = tax_unit("hi_modified_agi", period)

        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        phase_out_start = p_sli.phase_out.start[filing_status]
        # SEPARATE filers receive no Hawaii SLI deduction; we still need a
        # non-zero divisor here so the vectorized phase-out arithmetic does
        # not divide by zero. The where(separate, 0, ...) guard below masks
        # the result.
        phase_out_divisor = p_sli.phase_out.divisor[filing_status]
        reduction_share = min_(
            1, max_(0, (hi_magi - phase_out_start) / phase_out_divisor)
        )
        deduction = capped_interest * (1 - reduction_share)
        return where(separate, 0, deduction)


class hi_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii modified adjusted gross income for student loan interest phase-out"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = "https://files.hawaii.gov/tax/forms/current/n11ins.pdf#page=35"

    def formula(tax_unit, period, parameters):
        # Federal AGI plus Hawaii additions minus subtractions, excluding the
        # Hawaii student loan interest add/subtract pair to break the circular
        # reference. Federal AGI already subtracts the federal student loan
        # interest deduction, but the Hawaii worksheet uses Hawaii AGI before
        # any student loan interest deduction, so add the federal deduction back.
        p = parameters(period).gov.states.hi.tax.income
        other_additions = [
            v for v in p.additions.additions if v != "hi_student_loan_interest_addition"
        ]
        other_subtractions = [
            v
            for v in p.subtractions.subtractions
            if v != "hi_student_loan_interest_subtraction"
        ]
        other_additions_amount = (
            add(tax_unit, period, other_additions) if other_additions else 0
        )
        other_subtractions_amount = (
            add(tax_unit, period, other_subtractions) if other_subtractions else 0
        )
        federal_student_loan_interest_deduction = add(
            tax_unit, period, ["student_loan_interest_ald"]
        )
        return (
            tax_unit("adjusted_gross_income", period)
            + other_additions_amount
            - other_subtractions_amount
            + federal_student_loan_interest_deduction
        )


class hi_student_loan_interest_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest adjustment relative to federal AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = "https://files.hawaii.gov/tax/forms/current/n11ins.pdf#page=35"

    def formula(tax_unit, period, parameters):
        in_effect = parameters(
            period
        ).gov.states.hi.tax.income.subtractions.student_loan_interest.in_effect
        if not in_effect:
            return 0
        hawaii_deduction = tax_unit("hi_student_loan_interest_deduction", period)
        federal_deduction = tax_unit.sum(
            tax_unit.members("student_loan_interest_ald", period)
        )
        return hawaii_deduction - federal_deduction


class hi_student_loan_interest_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        adjustment = tax_unit("hi_student_loan_interest_adjustment", period)
        return max_(adjustment, 0)


class hi_student_loan_interest_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest addition"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        adjustment = tax_unit("hi_student_loan_interest_adjustment", period)
        return max_(0, -adjustment)
