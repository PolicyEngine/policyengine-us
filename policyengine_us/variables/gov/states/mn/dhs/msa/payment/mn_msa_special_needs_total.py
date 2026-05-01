from policyengine_us.model_api import *


class mn_msa_special_needs_total(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid total special-needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    adds = [
        "mn_msa_representative_payee_fee",
        "mn_msa_guardian_fee",
        "mn_msa_shelter_need_allowance",
        "mn_msa_housing_assistance",
    ]
