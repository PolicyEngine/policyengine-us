from policyengine_us.model_api import *


class ca_oc_general_relief_eligible_person_count(Variable):
    value_type = int
    entity = SPMUnit
    label = "Orange County General Relief eligible person count"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=04"
    # The MAP is based on the number of eligible persons in the GR Economic Unit
    # (Sec 80.2.d, Sec 80.3.a(2)). The MAP shall not include any child or any
    # member excluded for cause -- SSI/SSP, CalWORKs/CAPI, or noncitizen status --
    # so those people are not counted here.
    adds = ["ca_oc_general_relief_eligible_person"]
