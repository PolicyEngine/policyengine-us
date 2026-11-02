from policyengine_us.model_api import *


class nd_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "North Dakota LIHEAP eligible household size"
    reference = "https://www.nd.gov/dhs/policymanuals/415/415_20_10_50.htm"
    defined_for = StateCode.ND
    # SPMUnit approximates the energy-purchasing household. Foster/roomer
    # arrangements and qualified statuses absent from the input enum are not
    # reconstructed. Nonqualified members' income still counts.
    adds = ["is_citizen_or_legal_immigrant"]
