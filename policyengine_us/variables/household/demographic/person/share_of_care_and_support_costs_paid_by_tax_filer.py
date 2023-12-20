from policyengine_us.model_api import *


class share_of_care_and_support_costs_paid_by_tax_filer(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "The percentage of care and support costs of a senior paid by the tax filer"
