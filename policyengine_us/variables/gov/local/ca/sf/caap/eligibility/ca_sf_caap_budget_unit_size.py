from policyengine_us.model_api import *


class ca_sf_caap_budget_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "San Francisco County CAAP budget unit size"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    # Count the persons who can receive CAAP: those who are not SSI recipients
    # and have a qualified immigration status.
    adds = ["ca_sf_caap_eligible_person"]
