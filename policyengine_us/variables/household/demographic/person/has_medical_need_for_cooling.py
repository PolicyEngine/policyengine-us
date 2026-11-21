from policyengine_us.model_api import *


class has_medical_need_for_cooling(Variable):
    value_type = bool
    entity = Person
    label = "Has a certified medical need for home cooling"
    documentation = (
        "Whether a licensed medical practitioner certifies that this person's "
        "health will be seriously endangered unless the living quarters are "
        "cooled, for example through a physician's certification, a prescription "
        "for cooling, or a utility critical care (medical certification) form."
    )
    definition_period = YEAR
    default_value = False
