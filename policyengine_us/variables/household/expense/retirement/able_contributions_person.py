from policyengine_us.model_api import *


class able_contributions_person(Variable):
    value_type = float
    entity = Person
    label = "Person-level ABLE contributions"
    documentation = (
        "Contributions each person made, as the designated beneficiary, to "
        "their own ABLE account. The saver's credit counts only these."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/25B#d_1"
    unit = USD
    definition_period = YEAR
