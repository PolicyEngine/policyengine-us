from policyengine_us.model_api import *


class is_dc_tanf_related_to_head_or_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Person is related to head or spouse under the DC TANF regulations"
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a#(c)"  # (c-1)(1)
    default_value = True
