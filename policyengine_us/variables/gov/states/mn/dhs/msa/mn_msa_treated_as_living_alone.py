from policyengine_us.model_api import *


class mn_msa_treated_as_living_alone(Variable):
    value_type = bool
    entity = Person
    label = (
        "Whether the person is treated as living alone under Minnesota Supplemental Aid"
    )
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )
