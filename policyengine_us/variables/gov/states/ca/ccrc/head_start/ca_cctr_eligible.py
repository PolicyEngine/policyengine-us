from policyengine_us.model_api import *


class ca_cctr_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California General Child Care and Development eligible"
    definition_period = YEAR
    reference = (
        "https://www.ccrcca.org/headstart/programs/eligibility-requirements/"
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        ccrc_head_start_eligible = person(
            "ca_ccrc_head_start_eligible", period
        )
        recieves_early_head_start = person("early_head_start", period)
        return (recieves_early_head_start > 0) & ccrc_head_start_eligible
