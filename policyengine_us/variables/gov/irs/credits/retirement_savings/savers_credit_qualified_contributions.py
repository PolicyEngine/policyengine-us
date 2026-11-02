from policyengine_us.model_api import *


class savers_credit_qualified_contributions(Variable):
    value_type = float
    entity = Person
    label = "Retirement Savings Credit qualified contributions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25B#d_2",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=97",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        contributions = add(
            person, period, p.qualified_retirement_savings_contributions
        )
        # 25B(d)(2): from 2027, relevant ABLE distributions rather than
        # retirement-plan distributions.
        distributions = add(person, period, p.distributions)
        return max_(contributions - distributions, 0)
