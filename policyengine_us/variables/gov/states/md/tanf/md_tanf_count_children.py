from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0300-Technical-Eligibility/0307%20Age%20rev%2011.22.doc


class md_tanf_count_children(Variable):
    value_type = int
    entity = SPMUnit
    label = "Maryland TANF number of children"
    definition_period = YEAR
    defined_for = StateCode.MD
    adds = ["md_tanf_is_child"]
