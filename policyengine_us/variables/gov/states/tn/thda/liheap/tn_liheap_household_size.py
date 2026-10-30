from policyengine_us.model_api import *


class tn_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Tennessee LIHEAP household size"
    defined_for = StateCode.TN
    # PDF pages 9, 17-18
    reference = "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-2026-Policy-Manual-for-Tennessee.pdf#page=9"

    # Citizens and qualified noncitizens count in household size. Other
    # members are excluded from size, but their income counts in full in
    # tn_liheap_countable_income. Page 18 asks that benefits which can
    # reasonably be prorated be prorated by the number of eligible members,
    # and continues: "However, ineligible household members must be excluded
    # from the total household count when determining the benefit." The
    # matrix lookup at the reduced size is the method applied; prorating on
    # top of the size exclusion would reduce the benefit twice. SPM
    # membership approximates the LIHEAP household; Social Security number
    # refusal has no input.
    adds = ["is_citizen_or_legal_immigrant"]
