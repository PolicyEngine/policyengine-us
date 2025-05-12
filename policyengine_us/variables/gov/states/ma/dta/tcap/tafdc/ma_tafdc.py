from policyengine_us.model_api import *


class ma_tafdc(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = MONTH
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = "ma_tafdc_exceeds_eaedc"

    adds = ["ma_tafdc_if_claimed"]
