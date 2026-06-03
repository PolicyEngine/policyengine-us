from policyengine_us.model_api import *


class az_ccap_special_needs_child(Variable):
    value_type = bool
    entity = Person
    label = "Arizona Child Care Assistance Program special needs child"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-1210B.pdf#page=6",
        "https://des.az.gov/sites/default/files/dl/CCA-1210B.pdf#page=14",
    )

    def formula(person, period, parameters):
        return person("az_ccap_eligible_child", period) & person(
            "is_disabled", period.this_year
        )
