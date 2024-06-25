from policyengine_us.model_api import *


class amt_foreign_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "AMT foreign tax credit from Form 6251"
    unit = USD
    definition_period = YEAR
