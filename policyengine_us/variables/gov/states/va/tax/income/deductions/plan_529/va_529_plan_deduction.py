from policyengine_us.model_api import *


class va_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia deduction for contributions to Commonwealth Savers accounts"
    unit = USD
    definition_period = YEAR
    reference = (
        # Va. Code § 58.1-322.03(7): a deduction from Virginia adjusted gross
        # income in computing Virginia taxable income.
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-322.03/",
        # 2024 Form 760 instructions, deduction code 104 (Schedule ADJ line 8,
        # carried to Form 760 line 13)
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2024-760-instructions.pdf#page=28",
    )
    defined_for = StateCode.VA

    adds = ["va_529_plan_deduction_person"]
