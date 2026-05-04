from policyengine_us.model_api import *


class mn_msa_housing_assistance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Minnesota Supplemental Aid housing allowance"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002324&RevisionSelectionMethod=LatestReleased",
    )
    # TODO: model the § 256D.44 Subd. 5(g) eligibility test in a follow-up
    # PR — non-financial pathway (institution-relocation / HCBS-waiver /
    # chronic homelessness / housing stabilization), shelter cost > 40%
    # of unit gross income, and no concurrent housing subsidy. For now
    # this is a bare bool input.
