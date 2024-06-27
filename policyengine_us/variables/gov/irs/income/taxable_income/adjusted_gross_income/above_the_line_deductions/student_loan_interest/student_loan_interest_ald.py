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
        capped_interest = min_(interest, p.cap[filing_status])
        joint = filing_status == filing_status.possible_values.JOINT
        # Combine the income for units filing jointly
        modified_agi = person("student_loan_interest_ald_magi", period)
        combined_magi = where(
            joint,
            person.tax_unit.sum(modified_agi),
            modified_agi,
        )

        income_excess = max_(
            0, combined_magi - p.reduction.start[filing_status]
        )
        divisor = p.reduction.divisor[filing_status]
        reduction_rate = np.zeros_like(divisor)
        mask = divisor != 0
        reduction_rate[mask] = income_excess[mask] / divisor[mask]
        reduction_amount = capped_interest * reduction_rate
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return max_(capped_interest - reduction_amount, 0) * head_or_spouse
