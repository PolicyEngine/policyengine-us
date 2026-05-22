from policyengine_us.model_api import *


class student_loan_interest_ald(Variable):
    value_type = float
    entity = Person
    label = "Student loan interest ALD"
    unit = USD
    definition_period = YEAR
    documentation = "Above-the-line deduction for student loan interest"
    reference = "https://www.law.cornell.edu/uscode/text/26/221"
    defined_for = "student_loan_interest_ald_eligible"

    def formula(person, period, parameters):
        interest = person("student_loan_interest", period)
        p = parameters(period).gov.irs.ald.student_loan_interest
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        # IRC § 221(b)(1) caps the deduction at the return level, not per
        # spouse. Sum eligible filers' interest, cap at the return level,
        # then allocate the capped total back proportionally.
        eligible = person("student_loan_interest_ald_eligible", period)
        eligible_interest = interest * eligible
        tax_unit_interest = person.tax_unit.sum(eligible_interest)
        capped_tax_unit_interest = min_(tax_unit_interest, cap)
        share = np.divide(
            eligible_interest,
            tax_unit_interest,
            out=np.zeros_like(eligible_interest, dtype=float),
            where=tax_unit_interest > 0,
        )
        capped_interest = capped_tax_unit_interest * share
        joint = filing_status == filing_status.possible_values.JOINT
        # Combine the income for units filing jointly
        modified_agi = person("student_loan_interest_ald_magi", period)
        combined_magi = where(
            joint,
            person.tax_unit.sum(modified_agi),
            modified_agi,
        )
        reduction_start = p.reduction.start[filing_status]
        income_excess = max_(0, combined_magi - reduction_start)
        divisor = p.reduction.divisor[filing_status]
        reduction_rate = np.zeros_like(divisor)
        mask = divisor != 0
        reduction_rate[mask] = income_excess[mask] / divisor[mask]
        reduction_amount = capped_interest * reduction_rate
        return max_(capped_interest - reduction_amount, 0)
