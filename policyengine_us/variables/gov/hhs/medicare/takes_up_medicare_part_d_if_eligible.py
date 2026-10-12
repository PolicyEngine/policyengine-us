from policyengine_us.model_api import *


class takes_up_medicare_part_d_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether a Medicare enrollee takes up Medicare Part D"
    documentation = (
        "Whether a person enrolled in Medicare also enrolls in Part D drug "
        "coverage: a stand-alone prescription drug plan, a Medicare "
        "Advantage plan with drug coverage, or an employer group waiver plan. "
        "People whose drug coverage comes instead from a retiree drug subsidy "
        "plan, the Federal Employees Health Benefits Program, TRICARE for "
        "Life or the VA are not enrolled in Part D. Microdata assign this "
        "input; it defaults to true."
    )
    definition_period = YEAR
    default_value = True
