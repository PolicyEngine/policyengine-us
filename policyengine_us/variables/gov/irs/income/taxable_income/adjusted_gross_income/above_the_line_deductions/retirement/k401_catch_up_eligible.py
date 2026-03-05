from policyengine_us.model_api import *


class k401_catch_up_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for 401(k) catch-up contributions"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/26/1.414(v)-1#g_3_ii",
        "https://www.law.cornell.edu/uscode/text/26/414#v_5_A",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(
            period
        ).gov.irs.gross_income.retirement_contributions.catch_up
        return age >= p.age_threshold
