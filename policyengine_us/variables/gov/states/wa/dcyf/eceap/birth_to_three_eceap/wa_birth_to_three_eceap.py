from policyengine_us.model_api import *


class wa_birth_to_three_eceap(Variable):
    value_type = float
    entity = Person
    label = "Washington Birth to Three ECEAP"
    unit = USD
    definition_period = YEAR
    defined_for = "wa_birth_to_three_eceap_eligible"
    reference = (
        "https://fnspublic.ofm.wa.gov/FNSPublicSearch/GetPDF?packageID=74909#page=10"
    )
    adds = ["gov.states.wa.dcyf.eceap.birth_to_three_eceap.per_slot_rate"]
