from policyengine_us.model_api import *


class active_qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "Active qualified business income"
    documentation = (
        "Aggregate qualified business income from active qualified trades or "
        "businesses for the IRC §199A(i) minimum deduction."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#i"
