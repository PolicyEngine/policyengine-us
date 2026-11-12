from policyengine_us.model_api import *


class is_in_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "Person is currently in qualifying foster care"
    definition_period = MONTH
    documentation = (
        "Whether an authorized agency or court currently places this person "
        "in foster care, including placement with a caretaker household. "
        "Prior foster care alone does not establish current placement."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1758#b_12_A_vii"
