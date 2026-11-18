from policyengine_us.model_api import *


class vt_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Vermont LIHEAP eligible household size"
    defined_for = StateCode.VT
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=39",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2910.pdf",
    )

    # Rule 2914(a)(1) and P-2910 leave ineligible members, such as an
    # undocumented immigrant, out of the size while counting their income.
    adds = ["is_citizen_or_legal_immigrant"]
