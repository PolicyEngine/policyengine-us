from policyengine_us.model_api import *


class mn_msa_in_group_residential(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person resides in Group Residential Housing under Minnesota Supplemental Aid"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256I",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )
