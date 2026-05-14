from policyengine_us.model_api import *


class sstb_self_employment_income_would_be_qualified(Variable):
    value_type = bool
    entity = Person
    label = "SSTB self-employment income would be qualified"
    documentation = (
        "Whether SSTB self-employment income would count toward qualified "
        "business income before the §199A(d)(3) applicable-percentage phaseout."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c_3_A"
    default_value = True
