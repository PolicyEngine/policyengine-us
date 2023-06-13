from policyengine_us.model_api import *


class co_chp(Variable):
    value_type = float
    entity = Person
    label = "Child Health Plan Plus"
    definition_period = YEAR
    defined_for = "co_chp_eligible"
    adds = [
        "co_chp_ambulance_saving",
        "co_chp_er_visit_saving",
        "co_chp_inpatient_saving",
        "co_chp_lab_saving",
        "co_chp_outpatient_saving",
        "co_chp_physician_services_saving",
        "co_chp_prescription_saving",
        "co_chp_urgent_care_saving",
    ]
