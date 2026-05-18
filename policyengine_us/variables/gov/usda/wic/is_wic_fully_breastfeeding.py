from policyengine_us.model_api import *


class is_wic_fully_breastfeeding(Variable):
    value_type = bool
    entity = Person
    label = "Fully breastfeeding for WIC"
    documentation = (
        "Whether a breastfeeding WIC participant's infant receives no formula from WIC"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/246.10#e_7_i"
