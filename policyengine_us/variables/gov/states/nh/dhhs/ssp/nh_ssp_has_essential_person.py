from policyengine_us.model_api import *


class nh_ssp_has_essential_person(Variable):
    value_type = bool
    entity = Person
    label = "New Hampshire SSP certified needy essential person"
    definition_period = MONTH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = "A co-resident person essential to the recipient's well-being who does not qualify for assistance in their own right under He-W 601.05(p). Set on the recipient, not the caregiver; one caregiver is shared by an applicant couple."
