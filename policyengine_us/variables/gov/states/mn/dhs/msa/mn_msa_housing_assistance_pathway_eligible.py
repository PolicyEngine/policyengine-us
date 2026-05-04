from policyengine_us.model_api import *


class mn_msa_housing_assistance_pathway_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Meets a non-financial Minnesota Supplemental Aid housing assistance pathway"
    )
    documentation = "Whether the person meets one of the non-financial pathways for MSA Housing Assistance, such as transition from an institution, HCBS waiver eligibility, chronic homelessness, or housing stabilization."
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002324&RevisionSelectionMethod=LatestReleased",
    )
