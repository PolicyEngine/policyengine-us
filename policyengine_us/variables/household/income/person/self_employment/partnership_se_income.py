from policyengine_us.model_api import *


class partnership_se_income(Variable):
    value_type = float
    entity = Person
    label = "Partnership self-employment income"
    definition_period = YEAR
    documentation = "Partnership income subject to self-employment tax from Schedule K-1 Box 14. Only general partners' distributive share of trade/business income is included per 26 USC 1402(a)(13)."
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a_13"
