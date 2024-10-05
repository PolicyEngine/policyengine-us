from policyengine_us.model_api import *


class la_general_relief_disability_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Los Angeles County General Relief based on the disability requirements"
    # Person has to be disabled AND unable to work
    # which is curently not implemented
    defined_for = "is_disabled"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"
