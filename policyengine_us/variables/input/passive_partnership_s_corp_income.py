from policyengine_us.model_api import *


class passive_partnership_s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "Passive partnership and S-corporation income"
    unit = USD
    documentation = (
        "The section 469 passive subset of partnership_s_corp_income. This "
        "classifies income already counted in gross income and does not represent "
        "additional gross income."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#c_1_A_ii",
        "https://www.irs.gov/instructions/i8960",
    )
