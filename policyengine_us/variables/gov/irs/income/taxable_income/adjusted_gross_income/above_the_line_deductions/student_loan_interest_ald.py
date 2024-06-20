from policyengine_us.model_api import *


class student_loan_interest_ald(Variable):
    value_type = float
    entity = Person
    label = "Student loan interest ALD"
    unit = USD
    definition_period = YEAR
    documentation = "Above-the-line deduction for student loan interest"
    reference = "https://www.law.cornell.edu/uscode/text/26/221"

    def formula(person, period, parameters):
        interest = person("student_loan_interest", period)
        p = parameters(period).gov.irs.ald.student_loan_interest
        filing_status = person.tax_unit("filing_status", period)
        capped_interest = min_(interest, p.cap[filing_status])
        # The reduction is based on the taxpayer's modified adjusted gross income (MAGI)
        # which is defined as AGI less ALDs
        gross_income = add(person.tax_unit, period, ["irs_gross_income"])
        income_excess = max_(
            0, gross_income - p.reduction.start[filing_status]
        )
        divisor = p.reduction.divisor[filing_status]
        reduction_rate = np.zeros_like(divisor)
        mask = divisor != 0
        reduction_rate[mask] = income_excess[mask] / divisor[mask]
        reduction_amount = capped_interest * reduction_rate
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return max_(capped_interest - reduction_amount, 0) * head_or_spouse
