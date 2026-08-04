from policyengine_us.model_api import *


class nj_unemployment_insurance_spouse_employed_when_claim_established(Variable):
    value_type = bool
    entity = Person
    label = "New Jersey unemployment insurance claimant had an employed spouse when the claim was established"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
        "https://www.nj.gov/labor/ea/help/employer_handbook/ui.shtml",
    )
    defined_for = StateCode.NJ
