from policyengine_us.model_api import *


class il_isbe_was_teen_parent_at_first_birth(Variable):
    value_type = bool
    entity = Household
    label = "Parent was a teen at birth of first child"
    definition_period = YEAR
    documentation = (
        "Whether any parent in the household was under age 20 when their "
        "first child was born. This is a risk factor for Illinois ISBE "
        "early childhood programs."
    )
    reference = (
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf"
    )
    defined_for = StateCode.IL
