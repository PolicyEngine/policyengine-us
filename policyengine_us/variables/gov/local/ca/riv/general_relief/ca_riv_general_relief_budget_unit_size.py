from policyengine_us.model_api import *


class ca_riv_general_relief_budget_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Riverside County General Relief budget unit size"
    definition_period = MONTH
    defined_for = "in_riv"

    adds = ["spm_unit_size"]
    subtracts = ["ca_riv_general_relief_ineligible_person"]
