from policyengine_us.model_api import *


class nj_total_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey total deductions to income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        # NJ-1040 deductions, Form NJ-1040 lines 30-37c (medical expenses and
        # the New Jersey College Affordability Act deductions, line 37a).
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=26",
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-3-13/",
    )

    # nj_529_deduction (NJBEST contribution deduction, N.J.S.A. 54A:3-13, Form
    # NJ-1040 line 37a) reduces taxable income after the gross-income filing
    # threshold, alongside its 54A:3 sibling nj_medical_expense_deduction. See
    # issue #8849.
    adds = ["nj_medical_expense_deduction", "nj_529_deduction"]
