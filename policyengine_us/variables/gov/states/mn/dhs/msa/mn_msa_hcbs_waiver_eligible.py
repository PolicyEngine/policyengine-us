from policyengine_us.model_api import *


class mn_msa_hcbs_waiver_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for a Minnesota home and community-based services waiver"
    documentation = "Whether the person is eligible for a medical assistance home and community-based services waiver. Eligibility, not enrollment, places the person in the Minnesota Supplemental Aid living-alone standard (Minn. Stat. 256D.44 subd. 2)."
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44#stat.256D.44.2",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )
