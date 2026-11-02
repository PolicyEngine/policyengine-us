from policyengine_us.model_api import *


class hi_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Hawaii LIHEAP qualified household size"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/07/Policies-and-Procedures-2020.pdf#page=6",
    )
    # The SPM unit approximates the utility-sharing household. All members'
    # income remains countable, including members excluded from this size.
    adds = ["hi_liheap_qualified_member"]
