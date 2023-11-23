from policyengine_us.model_api import *


class la_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    label = "Los Angeles County General Relief"
    definition_period = MONTH
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"
