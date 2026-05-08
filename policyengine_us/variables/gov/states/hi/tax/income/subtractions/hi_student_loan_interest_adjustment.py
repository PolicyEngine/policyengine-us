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
        if period.start.year < 2025:
            return 0
        person = tax_unit.members
        eligible = person("student_loan_interest_ald_eligible", period)
        interest_paid = tax_unit.sum(person("student_loan_interest", period) * eligible)
        capped_interest = min_(interest_paid, 2_500)

        p = parameters(period).gov.states.hi.tax.income
        other_additions = [
            variable
            for variable in p.additions.additions
            if variable != "hi_student_loan_interest_addition"
        ]
        other_subtractions = [
            variable
            for variable in p.subtractions.subtractions
            if variable != "hi_student_loan_interest_subtraction"
        ]
        other_additions_amount = (
            add(tax_unit, period, other_additions) if len(other_additions) > 0 else 0
        )
        other_subtractions_amount = (
            add(tax_unit, period, other_subtractions)
            if len(other_subtractions) > 0
            else 0
        )
        hi_magi = tax_unit("adjusted_gross_income", period)
        hi_magi += other_additions_amount
        hi_magi -= other_subtractions_amount

        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        joint = filing_status == status.JOINT
        separate = filing_status == status.SEPARATE
        phase_out_start = where(joint, 100_000, 50_000)
        phase_out_divisor = where(joint, 30_000, 15_000)
        reduction_share = np.minimum(
            1.0, np.maximum(0.0, (hi_magi - phase_out_start) / phase_out_divisor)
        )
        deduction = capped_interest * (1 - reduction_share)
        return where(separate, 0, deduction)


class hi_student_loan_interest_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest adjustment relative to federal AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = "https://files.hawaii.gov/tax/forms/current/n11ins.pdf#page=35"

    def formula(tax_unit, period, parameters):
        if period.start.year < 2025:
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
