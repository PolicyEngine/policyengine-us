from policyengine_us.model_api import *

# reference:https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0300-Technical-Eligibility/0300%20Technical%20Eligibility%20Overview%20rev%2011.22.doc


class md_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland TANF eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
