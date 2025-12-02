from policyengine_us.model_api import *


class il_bcc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Persons with Breast or Cervical Cancer eligible"
    definition_period = YEAR
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=33528",
        "https://www.dhs.state.il.us/page.aspx?item=33527",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        is_female = person("is_female", period)
        age_eligible = person("il_bcc_age_eligible", period)
        immigration_eligible = person(
            "il_hfs_immigration_status_eligible", period
        )
        insurance_eligible = person("il_bcc_insurance_eligible", period)
        return (
            is_female
            & age_eligible
            & immigration_eligible
            & insurance_eligible
        )
