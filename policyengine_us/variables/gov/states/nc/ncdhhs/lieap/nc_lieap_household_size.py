from policyengine_us.model_api import *


class nc_lieap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina LIEAP eligible household size"
    defined_for = StateCode.NC
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/eps150.pdf",
        "https://policies.ncdhhs.gov/wp-content/uploads/eps175.pdf#page=1,4,5,6",
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=15,16",
    )

    def formula(spm_unit, period, parameters):
        # SPM units approximate residents sharing heat (EP-150). The generic
        # EP-175.01 requires one citizen/eligible alien; EP-300.10 excludes
        # ineligible members from size and specifies their income treatment.
        # The existing qualified-status variable cannot resolve all EP-175
        # document/PRUCOL categories, qualified-but-ineligible members, or
        # the optional inclusion of foster children. Those cases remain partial.
        return add(spm_unit, period, ["is_citizen_or_legal_immigrant"])
