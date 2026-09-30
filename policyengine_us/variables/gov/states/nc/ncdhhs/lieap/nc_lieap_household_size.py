from policyengine_us.model_api import *


class nc_lieap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina LIEAP eligible household size"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/eps150.pdf"

    def formula_2026(spm_unit, period, parameters):
        # SPM units approximate residents sharing heat (EP-150). The generic
        # status input cannot resolve all EP-175 document/PRUCOL categories or
        # the optional inclusion of foster children. Those cases remain partial.
        return add(spm_unit, period, ["is_citizen_or_legal_immigrant"])
