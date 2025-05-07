from policyengine_us.model_api import *


class ma_tafdc_if_claimed(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) benefit amount if claimed"
    definition_period = MONTH
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = "ma_tafdc_eligible"

    # The Infant Benefit and Clothing Allowance are mentioned in the TAFDC context
    # on the Mass.gov website: https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc
    adds = [
        "ma_tafdc_potential_main_benefit",
        "ma_tafdc_clothing_allowance",
        "ma_tafdc_infant_benefit",
    ]
