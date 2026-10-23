from policyengine_us.model_api import *


class total_disability_payments(Variable):
    value_type = float
    entity = Person
    label = "Disability (total) payments"
    unit = USD
    documentation = (
        "Disability income under IRC 22(c)(2)(B)(iii): wages or payments in lieu "
        "of wages for a period of absence from work due to permanent and total "
        "disability, from an employer's accident or health plan or pension plan "
        "that provides for disability retirement, to the extent included in "
        "gross income. Enter only the taxable part; it is also counted in "
        "employment_income or taxable_disability_benefits."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/22#c_2_B_iii"
    definition_period = YEAR
