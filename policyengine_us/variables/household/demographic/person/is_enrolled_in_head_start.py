from policyengine_us.model_api import *


class is_enrolled_in_head_start(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in a Head Start or Early Head Start program"
    definition_period = YEAR
    documentation = (
        "Whether this person enrolls in Head Start or Early Head Start. "
        "Enrollment differs from modeled eligibility and hypothetical take-up."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1758#b_12_A_iii",
        "https://fns-prod.azureedge.us/sites/default/files/cn/SP40_CACFP11_SFSP13-2013os.pdf",
    )
