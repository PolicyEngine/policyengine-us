from policyengine_us.model_api import *


class salt_refund_income(Variable):
    value_type = float
    entity = Person
    label = "State and local tax refund income"
    unit = USD
    definition_period = YEAR
    documentation = "Taxable state and local income tax refunds, credits, or offsets reported on Form 1040, Schedule 1, line 1."
    reference = "https://www.law.cornell.edu/uscode/text/26/111"
