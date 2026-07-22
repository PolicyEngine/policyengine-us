from policyengine_us.model_api import *


class va_educator_expenses(Variable):
    value_type = float
    entity = Person
    label = "Virginia eligible educator expenses"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    # Eligible educator qualifying expenses that were NOT reimbursed nor claimed
    # as a deduction on the federal return (Va. Code 58.1-322.03). The federal
    # educator deduction is above-the-line and already reflected in federal AGI,
    # and the baseline data do not identify this excess amount, so this is an
    # explicit input that defaults to $0 (as with the Ohio educator deduction).
    reference = "https://law.lis.virginia.gov/vacode/title58.1/section58.1-322.03/"
