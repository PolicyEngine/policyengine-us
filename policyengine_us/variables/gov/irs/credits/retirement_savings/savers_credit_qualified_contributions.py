from policyengine_us.model_api import *


class savers_credit_qualified_contributions(Variable):
    value_type = float
    entity = Person
    label = "Retirement Savings Credit qualified contributions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25B#d_2"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        contributions = add(
            person, period, p.qualified_retirement_savings_contributions
        )
        distributions = add(person, period, ["retirement_distributions"])
        return max_(contributions - distributions, 0)
