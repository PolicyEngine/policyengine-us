from policyengine_us.model_api import *


class tip_income(Variable):
    value_type = float
    entity = Person
    label = "Tip income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/26/31.3402(k)-1"

    # This variable only exists for the purpose of the tax_exempt_reform
