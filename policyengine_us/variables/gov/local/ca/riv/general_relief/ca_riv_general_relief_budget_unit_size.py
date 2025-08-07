from policyengine_us.model_api import *


class ca_riv_general_relief_budget_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Riverside County General Relief budget unit size"
    definition_period = MONTH
    defined_for = "in_riv"

    # Ineligible persons in the SPM Unit cannot receive GR benefits.
    # The number of ineligible person would never exceed the number of people in the SPM Unit.
    adds = ["spm_unit_size"]
    subtracts = ["ca_riv_general_relief_ineligible_person"]
