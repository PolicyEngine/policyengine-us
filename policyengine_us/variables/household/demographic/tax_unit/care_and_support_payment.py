from policyengine_us.model_api import *


class care_and_support_payment(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Amount of payment paid by filers for care and support"