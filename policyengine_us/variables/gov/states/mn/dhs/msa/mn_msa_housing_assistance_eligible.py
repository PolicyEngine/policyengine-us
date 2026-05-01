from policyengine_us.model_api import *


class mn_msa_housing_assistance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Minnesota Supplemental Aid housing allowance under § 256D.44 Subd. 5(g)"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002324&RevisionSelectionMethod=LatestReleased",
    )
    # Set to true if the person qualifies via EITHER pathway:
    #   (1) Subd. 5(g)(1) — institution-relocation, HCBS-waiver
    #       eligible, or shelter cost > 40% of income.
    #   (2) CM 0023.24 — chronic homelessness or housing
    #       stabilization.
    # The benefit amount is the same (1/2 x FBR) under either route.
