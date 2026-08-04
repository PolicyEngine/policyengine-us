from policyengine_us.model_api import *


class ira_contribution_limit(Variable):
    value_type = float
    entity = Person
    label = "IRA contribution limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions
        age = person("age", period)
        catch_up_eligible = age >= p.catch_up.age_threshold
        return p.limit.ira + where(
            catch_up_eligible,
            p.catch_up.limit.ira,
            0,
        )
