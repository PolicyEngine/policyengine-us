from policyengine_us.model_api import *


class is_aca_ptc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for ACA premium tax credit and pays ACA premium"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-2#b",
    )

    def formula(person, period, parameters):
        return person("pays_aca_premium", period) & person(
            "is_aca_ptc_eligible_before_premium", period
        )
