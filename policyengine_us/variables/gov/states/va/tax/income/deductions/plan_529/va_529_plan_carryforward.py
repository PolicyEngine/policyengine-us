from policyengine_us.model_api import *


class va_529_plan_carryforward(Variable):
    value_type = float
    entity = Person
    label = "Virginia Commonwealth Savers contributions carried forward"
    documentation = (
        "Contributions to Commonwealth Savers accounts this person owns, made "
        "in prior taxable years and not yet deducted, including carryovers "
        "succeeded to on a transfer of ownership."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # Va. Code § 58.1-322.03(7)(a)
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-322.03/",
        # 2024 Form 760 instructions, deduction code 104
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2024-760-instructions.pdf#page=28",
    )
