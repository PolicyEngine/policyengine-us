from policyengine_us.model_api import *


class educator_expense(Variable):
    value_type = float
    entity = Person
    label = "Educator expenses"
    unit = USD
    documentation = (
        "Unreimbursed qualified expenses an eligible educator paid: a "
        "kindergarten through grade 12 teacher, instructor, counselor, "
        "principal or aide in a school for at least 900 hours in the school "
        "year. Enter the full amount; the deduction applies the "
        "per-educator cap."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a_2_D",
        "https://www.law.cornell.edu/uscode/text/26/62#d_1",
    )
