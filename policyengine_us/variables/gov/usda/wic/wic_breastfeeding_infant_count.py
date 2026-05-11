from policyengine_us.model_api import *


class wic_breastfeeding_infant_count(Variable):
    value_type = int
    entity = Person
    label = "WIC breastfeeding infant count"
    documentation = (
        "Number of infants from the same pregnancy being breastfed by a WIC participant"
    )
    definition_period = MONTH
    default_value = 1
    reference = "https://www.law.cornell.edu/cfr/text/7/246.10#e_7_i"
