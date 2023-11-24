from policyengine_us.model_api import *


class la_general_relief_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Recipient of the Los Angeles County General Relief"
    definition_period = YEAR
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"
    default_value = False
