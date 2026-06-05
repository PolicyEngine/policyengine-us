from policyengine_us.model_api import *


class ca_sf_caap_budget_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "San Francisco County CAAP budget unit size"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    # Ineligible persons (e.g., SSI recipients or persons without a qualified
    # immigration status) cannot receive CAAP and are removed from the budget
    # unit. The number of ineligible persons never exceeds the SPM unit size.
    adds = ["spm_unit_size"]
    subtracts = ["ca_sf_caap_ineligible_person"]
