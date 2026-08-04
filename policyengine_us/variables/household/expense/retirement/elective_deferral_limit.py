from policyengine_us.model_api import *


class elective_deferral_limit(Variable):
    value_type = float
    entity = Person
    label = "401(k) and 403(b) elective deferral limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/402#g",
        "https://www.law.cornell.edu/uscode/text/26/414#v",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions
        base_limit = getattr(p.limit, "401k")
        catch_up_limit = person("k401_catch_up_limit", period)
        return base_limit + catch_up_limit
