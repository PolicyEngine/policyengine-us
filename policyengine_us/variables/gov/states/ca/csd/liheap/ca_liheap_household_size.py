from policyengine_us.model_api import *


class ca_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP qualified household size"
    defined_for = StateCode.CA
    # PDF pages 196,202-203
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=196"

    # The SPM unit approximates the household sharing energy costs. Income of
    # excluded nonqualified members remains countable.
    adds = ["is_citizen_or_legal_immigrant"]
