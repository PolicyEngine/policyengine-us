from policyengine_us.model_api import *


class mt_exemptions_count(Variable):
    value_type = int
    entity = Person
    label = "Number of Montana exemptions for each person"
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = [
        1,
        "is_blind",
        "mt_dependent_exemption_person",
        "mt_aged_exemption_person",
    ]
