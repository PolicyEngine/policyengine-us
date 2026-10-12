from policyengine_us.model_api import *


class ssi_receives_public_income_maintenance(Variable):
    value_type = bool
    entity = Person
    label = "Receives public income-maintenance payments for SSI purposes"
    documentation = (
        "Whether this person receives one of the public income-maintenance "
        "payments listed in 20 CFR 416.1142(a), such as TANF or need-based "
        "State or local assistance. SSI makes no ineligible-child "
        "allocation for a child who receives them (416.1163(b)). This input "
        "is not derived from modeled program benefits."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1142#p-416.1142(a)",
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(b)",
    )
