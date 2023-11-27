from policyengine_us.model_api import *


class la_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Los Angeles County General Relief"
    definition_period = MONTH
    defined_for = "la_general_relief_eligible"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    adds = ["la_general_relief_base_amount"]
    subtracts = ["la_general_relief_rent_contribution"]
