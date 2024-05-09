from policyengine_us.model_api import *


class savers_qualified_contributions(Variable):
    value_type = float
    entity = Person
    label = "Retirement Savings Credit qualified contributions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25B#d_2"
    adds = "gov.irs.credits.retirement_saving.qualified_retirement_savings_contributions"
    subtracts = ["retirement_distributions"]
