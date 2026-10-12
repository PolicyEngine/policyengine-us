from policyengine_us.model_api import *


class was_recently_incarcerated_for_medicaid_ce(Variable):
    value_type = bool
    entity = Person
    label = "Was recently incarcerated for Medicaid community engagement"
    documentation = (
        "Whether the person was an inmate of a public institution at any point "
        "during the three-month period relevant to the Medicaid community "
        "engagement incarceration exception."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=238",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/"
        "cib12082025.pdf#page=6",
    )
