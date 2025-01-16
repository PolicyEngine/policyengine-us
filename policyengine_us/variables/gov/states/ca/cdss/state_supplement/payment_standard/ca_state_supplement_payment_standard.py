from policyengine_us.model_api import *


class ca_state_supplement_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    adds = [
        "ca_state_supplement_dependent_amount",
        "ca_state_supplement_food_allowance",
        "ca_state_supplement_medical_care_facility_amount",
        "ca_state_supplement_out_of_home_care_facility_amount",
        "ca_state_supplement_aged_blind_disabled_amount",
    ]
