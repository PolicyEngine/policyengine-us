from policyengine_us.model_api import *


class mo_additions(Variable):
    value_type = float
    entity = Person
    label = "Missouri additions to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=12"
    defined_for = StateCode.MO
    adds = ["mo_other_additions"]
