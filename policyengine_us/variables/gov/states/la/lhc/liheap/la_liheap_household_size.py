from policyengine_us.model_api import *


class la_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Louisiana LIHEAP household size"
    defined_for = StateCode.LA
    reference = (
        # PDF pages 33-34
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=33",
        # PDF pages 40-41
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=40",
    )

    # Citizens and qualified noncitizens count in household size. Undocumented
    # members are excluded from size, but their income counts in full in
    # la_liheap_countable_income. SPM membership approximates the LIHEAP
    # household; Social Security number verification and the member
    # exclusions of the April 2026 guide have no inputs.
    adds = ["is_citizen_or_legal_immigrant"]
