from policyengine_us.model_api import *


class de_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Delaware LIHEAP eligible household size"
    defined_for = StateCode.DE
    reference = "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=40"

    # Historical DEAP manual section 426 counts only qualified members in
    # household size, but retains every member's countable income. The FY2026
    # plan does not restate or replace this allocation rule.
    adds = ["is_citizen_or_legal_immigrant"]
