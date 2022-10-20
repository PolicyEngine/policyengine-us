from policyengine_us.model_api import *


class foreign_earned_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign earned income ALD"
    unit = USD
    documentation = "Income earned and any housing expense in foreign countries that is excluded from adjusted gross income under 26 U.S. Code § 911."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/911"
