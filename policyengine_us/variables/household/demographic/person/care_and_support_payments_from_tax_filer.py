from policyengine_us.model_api import *


class care_and_support_payments_from_tax_filer(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = "Amount of payments made by the tax filer for this person's care and support"
