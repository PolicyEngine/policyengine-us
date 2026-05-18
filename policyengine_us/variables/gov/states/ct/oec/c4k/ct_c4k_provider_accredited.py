from policyengine_us.model_api import *


class ct_c4k_provider_accredited(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Whether the child's Care 4 Kids provider is accredited"
    reference = (
        "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-13/",
        "https://www.cga.ct.gov/2020/rpt/pdf/2020-R-0274.pdf#page=1",
    )
